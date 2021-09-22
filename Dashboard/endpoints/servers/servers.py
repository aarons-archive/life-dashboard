# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

# My stuff
from core import values
from core.app import Dashboard


@aiohttp_jinja2.template("servers.html")  # type: ignore
async def servers(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: Dashboard = request.app  # type: ignore
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return values.LOGIN_URL

    related_guilds = await app.get_related_guilds(session, user_id=user.id)

    return {
        **app.links,
        "user": user.to_dict(),
        **related_guilds
    }


@aiohttp_jinja2.template("server.html")  # type: ignore
async def server(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: Dashboard = request.app  # type: ignore
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return values.LOGIN_URL

    related_guilds = await app.get_related_guilds(session, user_id=user.id, guild_id=int(request.match_info["guild_id"]))
    if not related_guilds["guild"]:
        return aiohttp.web.Response(text="that server doesn't exist or you don't have access to it.", status=401)

    return {
        **app.links,
        "user": user.to_dict(),
        **related_guilds
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/servers", servers),  # type: ignore
            aiohttp.web.get(r"/servers/{guild_id:\d+}", server),  # type: ignore
        ]
    )
