# Future
from __future__ import annotations

# Packages
import aiohttp.web
import aiohttp_session

# My stuff
from core.app import Dashboard


async def logout(request: aiohttp.web.Request) -> aiohttp.web.Response:

    app: Dashboard = request.app  # type: ignore
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return aiohttp.web.HTTPFound("/")

    await app.db.execute("UPDATE users SET spotify_refresh_token = $1 WHERE id = $2", None, user.id)
    try:
        del app.spotify_user_credentials[user.id]
    except KeyError:
        pass

    return aiohttp.web.HTTPFound("/")


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/spotify/logout", logout)
        ]
    )
