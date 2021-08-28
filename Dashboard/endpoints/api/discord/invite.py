import aiohttp.web
import discord

from core import config, values


async def invite(request: aiohttp.web.Request) -> aiohttp.web.Response:

    class Snowflake:

        def __init__(self, id: int) -> None:
            self.id = id


    return aiohttp.web.HTTPFound(
        discord.utils.oauth_url(
            client_id=config.CLIENT_ID,
            permissions=values.PERMISSIONS,
            guild=Snowflake(request.match_info["guild_id"]),  # type: ignore
            redirect_uri=config.INVITE_REDIRECT,
            scopes=["bot", "applications.commands"],
        )
    )


async def invite_callback(request: aiohttp.web.Request) -> aiohttp.web.Response:

    if guild_id := request.query.get("guild_id"):
        return aiohttp.web.HTTPFound(config.redirect_uri(f"/servers/{guild_id}"))

    elif error := request.query.get("error"):
        return aiohttp.web.Response(text=f"you cancelled the bot invite: {error}", status=400)

    return aiohttp.web.Response(text="?", status=400)


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/discord/invite/{guild_id:\d+}", invite),
            aiohttp.web.get(r"/api/discord/invite/callback", invite_callback)
        ]
    )
