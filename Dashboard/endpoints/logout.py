import aiohttp.web
import aiohttp_session


async def logout(request: aiohttp.web.Request) -> None:

    session = await aiohttp_session.get_session(request)
    session.invalidate()

    raise aiohttp.web.HTTPFound("/")


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/logout", logout)])  # type: ignore
