# Future
from __future__ import annotations

# Standard Library
import secrets

# Packages
import aiohttp.web
import aiohttp_session

# My stuff
from core import config, values
from core.app import Dashboard


async def login(request: aiohttp.web.Request) -> aiohttp.web.Response:

    session = await aiohttp_session.new_session(request)

    state = secrets.token_urlsafe(20)
    session["discord_state"] = state

    return aiohttp.web.HTTPFound(
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={config.CLIENT_ID}"
        f"&response_type=code"
        f"&scope=identify+guilds"
        f"&redirect_uri={config.LOGIN_REDIRECT}"
        f"&state={state}"
    )


async def login_callback(request: aiohttp.web.Request) -> aiohttp.web.Response:

    if error := request.query.get("error"):
        return aiohttp.web.Response(text=f"you cancelled the login prompt: {error}", status=400)

    session = await aiohttp_session.get_session(request)

    if session.get("discord_state") != request.query.get("state"):
        return aiohttp.web.Response(text="'state' query parameters do not match.", status=400)

    app: Dashboard = request.app  # type: ignore

    async with app.session.post(
            url="https://discord.com/api/oauth2/token",
            data={
                "client_id":     config.CLIENT_ID,
                "client_secret": config.CLIENT_SECRET,

                "grant_type":    "authorization_code",
                "code":          request.query["code"],
                "redirect_uri":  config.LOGIN_REDIRECT,

                "scope":         "identify guilds",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
    ) as response:

        if response.status != 200:
            return aiohttp.web.Response(text="something went wrong while authenticating with discord.", status=400)

        session["token"] = await response.json()

    return values.ROOT_URL


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/discord/login", login),
            aiohttp.web.get(r"/api/discord/login/callback", login_callback)
        ]
    )
