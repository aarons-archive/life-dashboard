import secrets

import aiohttp.web
import aiohttp_session

from core import config


async def login(request: aiohttp.web.Request) -> None:

    session = await aiohttp_session.get_session(request)

    state = secrets.token_urlsafe(20)
    session["state"] = state

    raise aiohttp.web.HTTPFound(
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={config.CLIENT_ID}"
        f"&response_type=code"
        f"&scope=identify+guilds"
        f"&redirect_uri={config.LOGIN_CALLBACK}"
        f"&state={state}"
    )


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/login", login)])  # type: ignore
