from typing import Any, Optional

import aiohttp.web
import aiohttp_jinja2

from core.app import Dashboard


class Index:

    @aiohttp_jinja2.template("index.html")
    async def index(self, request: aiohttp.web.Request) -> Optional[dict[str, Any]]:

        app: Dashboard = request.app
        return await app.ipc.request("basic_information")


def setup(app: aiohttp.web.Application):

    index = Index()

    app.add_routes([
        aiohttp.web.get(r"/", index.index),
    ])
