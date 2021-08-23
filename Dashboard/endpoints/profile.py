from typing import Any, Optional

import aiohttp.web
import aiohttp_jinja2


@aiohttp_jinja2.template("profile.html")
async def servers(request: aiohttp.web.Request) -> Optional[dict[str, Any] | aiohttp.web.Response]:
    return None


def setup(app: aiohttp.web.Application):

    app.add_routes(
        [
            aiohttp.web.get(r"/profile/", servers),
        ]
    )
