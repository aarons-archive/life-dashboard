import aiohttp.web
import aiohttp_session


async def logout(request: aiohttp.web.Request) -> aiohttp.web.Response:

    session = await aiohttp_session.get_session(request)
    session.invalidate()

    return aiohttp.web.HTTPFound("/")


def setup(app: aiohttp.web.Application):

    app.add_routes(
        [
            aiohttp.web.get(r"/logout", logout),
        ]
    )
