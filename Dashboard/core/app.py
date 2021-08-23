import json
import logging
from typing import Optional

import aiohttp
import aiohttp.web
import aiohttp_session
import aioredis
import asyncpg
from aiohttp_session import redis_storage
from discord.ext import ipc

from core import config
from utilities import http, objects


__log__ = logging.getLogger("dashboard")


class Dashboard(aiohttp.web.Application):

    def __init__(self) -> None:
        super().__init__()

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        self.db: Optional[asyncpg.Pool] = None
        self.redis: Optional[aioredis.Redis] = None
        self.ipc: ipc.Client = ipc.Client(secret_key=config.SECRET_KEY)

        self.http = http.HTTPClient(session=self.session)

        self.on_startup.append(self.start)

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

    async def get_token(self, session: aiohttp_session.Session) -> Optional[objects.Token]:

        if not (data := session.get("token")):
            return None

        token = objects.Token(data=data)

        if token.is_expired():

            async with self.session.post(
                    url="https://discord.com/api/oauth2/token",
                    data={
                        "client_secret": config.CLIENT_SECRET,
                        "client_id":     config.CLIENT_ID,
                        "redirect_uri":  config.LOGIN_CALLBACK,
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

    async def fetch_user(self, session: aiohttp_session.Session) -> Optional[objects.User]:

        if not (token := await self.get_token(session)):
            return None

        data = await self.http.request(http.Route("GET", "/users/@me", token=token.access_token))
        user = objects.User(data=data)

        session["user"] = user.to_json()

        return user

    async def get_user(self, session: aiohttp_session.Session) -> Optional[objects.User]:

        if not (data := session.get("user")):
            user = await self.fetch_user(session)

        else:
            user = objects.User(data=json.loads(data))
            if user.is_expired():
                user = await self.fetch_user(session)

        return user

    async def fetch_guilds(self, session: aiohttp_session.Session) -> Optional[list[objects.Guild]]:

        if not (token := await self.get_token(session)):
            return None

        data = await self.http.request(http.Route("GET", "/users/@me/guilds", token=token.access_token))
        guilds = [objects.Guild(data=guild_data) for guild_data in data]

        session["guilds"] = [guild.to_json() for guild in guilds]

        return guilds

    async def get_guilds(self, session: aiohttp_session.Session) -> Optional[list[objects.Guild]]:

        if not (data := session.get("guilds")):
            guilds = await self.fetch_guilds(session)

        else:
            guilds = [objects.Guild(data=json.loads(guild_data)) for guild_data in data]
            if any(guild.is_expired() for guild in guilds):
                guilds = await self.fetch_guilds(session)

        return guilds
