from typing import Any, Optional

import aiohttp.web
import aiohttp_jinja2
import aiohttp_session

from core.app import Dashboard


@aiohttp_jinja2.template("index.html")  # type: ignore
async def index(request: aiohttp.web.Request) -> dict[str, Any] | None:

    session = await aiohttp_session.get_session(request)

    app: Dashboard = request.app  # type: ignore
    user = await app.get_user(session)

    stats = await app.ipc.request("stats")

    return {
        **app.links,
        **stats,
        "user": user.to_dict() if user else None
    }


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/", index)])  # type: ignore
