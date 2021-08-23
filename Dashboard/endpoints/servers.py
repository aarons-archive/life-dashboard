from typing import Any, Optional

import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

from core.app import Dashboard


@aiohttp_jinja2.template("servers.html")  # type: ignore
async def servers(request: aiohttp.web.Request) -> Optional[dict[str, Any] | aiohttp.web.Response]:

    app: Dashboard = request.app
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return aiohttp.web.HTTPFound("/login")

    guilds = await app.get_guilds(session)

    mutual_guild_ids = await app.ipc.request("mutual_guild_ids", user_id=user.id)

    mutual_guilds = [guild.to_dict() for guild in guilds if guild.id in mutual_guild_ids]
    non_mutual_guilds = [guild.to_dict() for guild in guilds if guild.id not in mutual_guild_ids]

    return {
        "user":              user.to_dict(),
        "mutual_guilds":     mutual_guilds,
        "non_mutual_guilds": non_mutual_guilds,
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/servers", servers)])  # type: ignore