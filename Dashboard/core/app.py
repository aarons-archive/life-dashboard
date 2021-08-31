# Future
from __future__ import annotations

# Standard Library
import logging
import time
from typing import TYPE_CHECKING

# Packages
import aiohttp
import aiohttp.web
import aiohttp_session
import aioredis
import asyncpg
import discord.utils
from aiohttp_session import redis_storage
from discord.ext import ipc

# My stuff
from core import config, values
from utilities import http, objects


if TYPE_CHECKING:
    # Standard Library
    from typing import Any, Optional

    # My stuff
    from typings.utilities.objects.guild import RelatedGuilds
    from typings.utilities.objects.user import UserResponse


__log__: logging.Logger = logging.getLogger("dashboard")


class Dashboard(aiohttp.web.Application):

    def __init__(self) -> None:
        super().__init__()

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        self.db: asyncpg.Pool | None = None
        self.redis: aioredis.Redis | None = None

        self.ipc: ipc.Client = ipc.Client(secret_key=config.SECRET_KEY, multicast_port=config.MULTICAST_PORT)
        self.http: http.HTTPClient = http.HTTPClient(session=self.session)

        self.on_startup.append(self.start)

        self.links: dict[str, Any] = {
            "invite_link": values.INVITE_LINK
        }

    async def start(self, _) -> None:

        try:
            __log__.debug("[POSTGRESQL] Attempting connection.")
            db = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)
        except Exception as e:
            __log__.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[POSTGRESQL] Successful connection.")
            self.db = db

        try:
            __log__.debug("[REDIS] Attempting connection.")
            redis = aioredis.from_url(url=config.REDIS, retry_on_timeout=True)
            await redis.ping()
        except (aioredis.ConnectionError, aioredis.ResponseError) as e:
            __log__.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[REDIS] Successful connection.")
            self.redis = redis

        aiohttp_session.setup(
            app=self,
            storage=redis_storage.RedisStorage(redis)
        )

        self.links |= await self.ipc.request("links")

    #

    async def get_token(
        self,
        session: aiohttp_session.Session,
        /
    ) -> objects.Token | None:

        if not (data := session.get("token")):
            return None

        token = objects.Token(data=data)

        if token.is_expired():

            async with self.session.post(
                    url="https://discord.com/api/oauth2/token",
                    data={
                        "client_secret": config.CLIENT_SECRET,
                        "client_id":     config.CLIENT_ID,
                        "redirect_uri":  config.LOGIN_REDIRECT,
                        "refresh_token": token.refresh_token,
                        "grant_type":    "refresh_token",
                        "scope":         "identify guilds",
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
            ) as response:

                if response.status != 200:
                    raise Exception  # TODO: Raise a better exception

                data = await response.json()

            if error := data.get("error"):
                raise Exception(error)  # TODO: Raise a better exception

            token = objects.Token(data)
            session["token"] = token.to_json()

        return token

    #

    async def fetch_user(
        self,
        session: aiohttp_session.Session,
        /
    ) -> objects.User | None:

        if not (token := await self.get_token(session)):
            return None

        data: UserResponse = await self.http.request(http.Route("GET", "/users/@me", token=token.access_token))
        data["fetched_at"] = time.time()

        session["user"] = data

        return objects.User(data)

    async def get_user(
        self,
        session: aiohttp_session.Session,
        /
    ) -> objects.User | None:

        if not (data := session.get("user")):
            return await self.fetch_user(session)

        user = objects.User(data)

        if user.is_expired():
            user = await self.fetch_user(session)

        return user

    #

    async def fetch_user_guilds(
        self,
        session: aiohttp_session.Session,
        /
    ) -> dict[int, objects.Guild] | None:

        if not (token := await self.get_token(session)):
            return None

        guilds_data = await self.http.request(http.Route("GET", "/users/@me/guilds", token=token.access_token))

        for guild_data in guilds_data:
            guild_data["fetched_at"] = time.time()

        session["guilds"] = guilds_data

        return {int(data["id"]): objects.Guild(data) for data in guilds_data}

    async def get_user_guilds(
        self,
        session: aiohttp_session.Session,
        /
    ) -> dict[int, objects.Guild] | None:

        if not (guilds_data := session.get("guilds")):
            return await self.fetch_user_guilds(session)

        guilds = {int(data["id"]): objects.Guild(data) for data in guilds_data}

        if any(guild.is_expired() for guild in guilds.values()):
            guilds = await self.fetch_user_guilds(session)

        return guilds

    #

    async def get_related_guilds(
        self,
        session: aiohttp_session.Session,
        /,
        *,
        user_id: int,
        guild_id: Optional[int] = None
    ) -> RelatedGuilds:

        data: RelatedGuilds = {
            "mutual_guilds":     None,
            "non_mutual_guilds": None,
            "guild":             None
        }

        if not (guilds := await self.get_user_guilds(session)):
            return data

        mutual_guild_ids = await self.ipc.request("mutual_guild_ids", user_id=user_id)

        data["mutual_guilds"] = [guild.to_dict() for guild in guilds.values() if guild.id in mutual_guild_ids]
        data["non_mutual_guilds"] = [guild.to_dict() for guild in guilds.values() if guild.id not in mutual_guild_ids]

        if guild_id and (guild := discord.utils.get([guild for guild in guilds.values() if guild.id in mutual_guild_ids], id=guild_id)):
            data["guild"] = guild.to_dict()

        return data
