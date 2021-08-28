import aiohttp.web
import aiohttp_session

from core import config
from core.app import Dashboard


async def login_callback(request: aiohttp.web.Request) -> aiohttp.web.Response:

    if error := request.query.get("error"):
        return aiohttp.web.Response(text=f"you cancelled the login prompt: {error}", status=400)

    session = await aiohttp_session.get_session(request)

    if session.get("state") != request.query.get("state"):
        return aiohttp.web.Response(text=f"'state' query parameters do not match.", status=400)

    del session["state"]

    app: Dashboard = request.app  # type: ignore

    async with app.session.post(
            url=f"https://discord.com/api/oauth2/token",
            data={
                "client_secret": config.CLIENT_SECRET,
                "client_id":     config.CLIENT_ID,
                "redirect_uri":  config.LOGIN_REDIRECT,
                "code":          request.query["code"],
                "grant_type":    "authorization_code",
                "scope":         "identify guilds",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
    ) as response:

        if response.status != 200:
            return aiohttp.web.Response(text=f"something went wrong while authenticating with discord.", status=400)

        session["token"] = await response.json()

    return aiohttp.web.HTTPFound("/")


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/discord/login/callback", login_callback)
        ]
    )
