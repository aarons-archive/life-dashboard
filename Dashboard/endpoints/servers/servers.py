from typing import Any

import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

from core.app import Dashboard


@aiohttp_jinja2.template("servers.html")  # type: ignore
async def servers(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: Dashboard = request.app  # type: ignore
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return aiohttp.web.HTTPFound("/login")

    guilds = await app.get_user_guilds(session)
    mutual_guild_ids = await app.ipc.request("mutual_guild_ids", user_id=user.id)

    mutual_guilds = [guild.to_dict() for guild in guilds if guild.id in mutual_guild_ids]
    non_mutual_guilds = [guild.to_dict() for guild in guilds if guild.id not in mutual_guild_ids]

    return {
        **app.links,
        "user":              user.to_dict(),
        "mutual_guilds":     mutual_guilds,
        "non_mutual_guilds": non_mutual_guilds,
    }


@aiohttp_jinja2.template("server.html")  # type: ignore
async def server(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: Dashboard = request.app  # type: ignore
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return aiohttp.web.HTTPFound("/login")

    guilds = await app.get_user_guilds(session)
    mutual_guild_ids = await app.ipc.request("mutual_guild_ids", user_id=user.id)

    mutual_guilds = {guild.id: guild.to_dict() for guild in guilds if guild.id in mutual_guild_ids}

    if not (guild := mutual_guilds.get(int(request.match_info["guild_id"]))):
        return aiohttp.web.Response(text=f"that server doesn't exist or you don't have access to it.", status=401)

    return {
        **app.links,
        "user": user.to_dict(),
        "guild": guild,
        "mutual_guilds": list(mutual_guilds.values())
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/servers", servers),  # type: ignore
            aiohttp.web.get(r"/servers/{guild_id:\d+}", server),  # type: ignore
        ]
    )
