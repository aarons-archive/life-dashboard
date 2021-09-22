# Future
from __future__ import annotations

# Standard Library
import secrets

# Packages
import aiohttp.web
import aiohttp_session
import aiospotify

# My stuff
from core import config, values
from core.app import Dashboard


async def spotify_login(request: aiohttp.web.Request) -> aiohttp.web.Response:

    session = await aiohttp_session.get_session(request)

    state = secrets.token_urlsafe(20)
    session["spotify_state"] = state

    return aiohttp.web.HTTPFound(
        f"https://accounts.spotify.com/authorize/?"
        f"client_id={config.SPOTIFY_CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri={config.SPOTIFY_LOGIN_REDIRECT}&"
        f"state={state}&"
        f"scope=playlist-read-private%20playlist-read-collaborative%20user-read-private%20user-read-playback-state%20user-read-currently-playing%20"
        f"user-library-read%20user-read-playback-position%20user-read-recently-played%20user-top-read%20&"
        f"show_dialog=True"
    )


async def spotify_login_callback(request: aiohttp.web.Request) -> aiohttp.web.Response:

    if error := request.query.get("error"):
        return aiohttp.web.Response(text=f"you cancelled the login prompt: {error}", status=400)

    session = await aiohttp_session.get_session(request)

    if session.get("spotify_state") != request.query.get("state"):
        return aiohttp.web.Response(text="'state' query parameters do not match.", status=400)

    app: Dashboard = request.app  # type: ignore

    if not (user := await app.get_user(session)):
        return aiohttp.web.Response(text="you are not logged in with discord.", status=400)

    async with app.session.post(
            url="https://accounts.spotify.com/api/token",
            data={
                "client_id":     config.SPOTIFY_CLIENT_ID,
                "client_secret": config.SPOTIFY_CLIENT_SECRET,

                "grant_type":    "authorization_code",
                "code":          request.query["code"],
                "redirect_uri":  config.SPOTIFY_LOGIN_REDIRECT,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
    ) as response:

        if response.status != 200:
            return aiohttp.web.Response(text="something went wrong while authenticating with spotify.", status=400)

        data = await response.json()

        await app.db.execute("UPDATE users SET spotify_refresh_token = $1 WHERE id = $2", data["refresh_token"], user.id)
        app.spotify_user_credentials[user.id] = aiospotify.UserCredentials(data, config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET)

    return values.PROFILE_URL


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes(
        [
            aiohttp.web.get(r"/api/spotify/login", spotify_login),
            aiohttp.web.get(r"/api/spotify/login/callback", spotify_login_callback)
        ]
    )
