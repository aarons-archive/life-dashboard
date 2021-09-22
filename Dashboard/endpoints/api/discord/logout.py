# Future
from __future__ import annotations

# Packages
import aiohttp.web
import aiohttp_session

# My stuff
from core import values


async def logout(request: aiohttp.web.Request) -> aiohttp.web.Response:

    session = await aiohttp_session.get_session(request)
    session.invalidate()

    return values.ROOT_URL


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/discord/logout", logout)
        ]
    )
