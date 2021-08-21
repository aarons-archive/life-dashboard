import aiohttp.web
import aiohttp_session

from core import config
from core.app import Dashboard


async def discord_callback(request: aiohttp.web.Request) -> aiohttp.web.Response:

    session = await aiohttp_session.get_session(request)

    if session.get("state") != request.query["state"]:
        return aiohttp.web.json_response({'error': "'state' query parameters do not match."}, status=400)

    del session["state"]

    app: Dashboard = request.app

    async with app.session.post(
            url=f"https://discord.com/api/oauth2/token",
            data={
                "client_secret": config.CLIENT_SECRET,
                "client_id":     config.CLIENT_ID,
                "redirect_uri":  config.LOGIN_CALLBACK,
                "code":          request.query["code"],
                "grant_type":    "authorization_code",
                "scope":         "identify guilds",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
    ) as response:

        if response.status != 200:
            return aiohttp.web.json_response({'error': "something went wrong while authenticating with discord."}, status=400)

        data = await response.json()

    session["token"] = data

    if not (url := session.get("login_redirect")):
        url = "/"
    else:
        del session["login_redirect"]

    raise aiohttp.web.HTTPFound(url)


def setup(app: aiohttp.web.Application):
    app.add_routes(
        [
            aiohttp.web.get(r"/api/discord-callback", discord_callback),
        ]
    )
