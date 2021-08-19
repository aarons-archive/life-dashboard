import logging
from typing import Optional

import aiohttp
import aiohttp.web
import aioredis
import asyncpg

from discord.ext import ipc
from core import config


__log__ = logging.getLogger("dashboard")


class Dashboard(aiohttp.web.Application):

    def __init__(self) -> None:
        super().__init__()

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        self.db: Optional[asyncpg.Pool] = None
        self.redis: Optional[aioredis.client.StrictRedis] = None
        self.ipc: ipc.Client = ipc.Client(secret_key=config.SECRET_KEY)

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
            redis = aioredis.from_url(url=config.REDIS, decode_responses=True, retry_on_timeout=True)
            await redis.ping()
        except (aioredis.ConnectionError, aioredis.ResponseError) as e:
            __log__.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[REDIS] Successful connection.")
            self.redis = redis
