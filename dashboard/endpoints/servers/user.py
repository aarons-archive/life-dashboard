# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

# My stuff
from core.app import Dashboard


@aiohttp_jinja2.template("user.html")  # type: ignore
async def user(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: Dashboard = request.app  # type: ignore
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return aiohttp.web.HTTPFound("/api/discord/login")

    additional_user_info = await app.ipc.request("additional_user_info", user_id=user.id)

    return {
        **user,
        **additional_user_info
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/servers/{guild_id:\d+}/user/{user_id:\d+}", user)])  # type: ignore
