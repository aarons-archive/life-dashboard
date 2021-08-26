import aiohttp.web
import discord

from core import config, values


async def invite(request: aiohttp.web.Request) -> aiohttp.web.Response:

    if guild_id := request.query.get("guild_id"):
        return aiohttp.web.HTTPFound(config.redirect_uri(f"/servers/{guild_id}"))

    elif request.query.get("error"):
        return aiohttp.web.json_response(
            data={"error": "you cancelled the bot invite prompt"},
            status=400
        )  # TODO: Better error here.

    class GoAndFuckYourselfDpy:

        def __init__(self, id: int) -> None:
            self.id = id

    return aiohttp.web.HTTPFound(
        discord.utils.oauth_url(
            client_id=config.CLIENT_ID,
            permissions=values.PERMISSIONS,
            guild=GoAndFuckYourselfDpy(request.match_info["guild_id"]),  # type: ignore
            redirect_uri=config.redirect_uri("/api/discord/invite"),
            scopes=["bot", "applications.commands"],
        )
    )


def setup(app: aiohttp.web.Application):
    app.add_routes(
        [
            aiohttp.web.get(r"/api/discord/invite/{guild_id:\d+}", invite),
            aiohttp.web.get(r"/api/discord/invite", invite)
        ]
    )
