from typing import Any, Optional

import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

from core.app import Dashboard


@aiohttp_jinja2.template("index.html")
async def index(request: aiohttp.web.Request) -> Optional[dict[str, Any]]:

    app: Dashboard = request.app

    session = await aiohttp_session.get_session(request)

    #data = await app.ipc.request("basic_information")
    data = await app.get_user(session)
    return data.to_dict()


def setup(app: aiohttp.web.Application):

    app.add_routes([
        aiohttp.web.get(r"/", index),
    ])
