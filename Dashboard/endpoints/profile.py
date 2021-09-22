# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

# My stuff
from core import values
from core.app import Dashboard


@aiohttp_jinja2.template("profile.html")  # type: ignore
async def profile(request: aiohttp.web.Request) -> dict[str, Any] | aiohttp.web.Response | None:

    app: Dashboard = request.app  # type: ignore
    session = await aiohttp_session.get_session(request)

    if not (user := await app.get_user(session)):
        return values.LOGIN_URL

    related_guilds = await app.get_related_guilds(session, user_id=user.id)

    if not (credentials := await app.get_spotify_credentials(session)):
        data = {}
    else:
        data = await app.spotify.http.get_current_user_profile(credentials=credentials)

    return {
        **app.links,
        "user": user.to_dict(),
        **related_guilds,
        "data": data
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/profile", profile)])  # type: ignore
