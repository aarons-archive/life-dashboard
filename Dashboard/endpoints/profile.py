from typing import Any, Optional

import aiohttp.web
import aiohttp_jinja2


@aiohttp_jinja2.template("profile.html")  # type: ignore
async def profile(_: aiohttp.web.Request) -> Optional[dict[str, Any] | aiohttp.web.Response]:
    return None


def setup(app: aiohttp.web.Application) -> None:
    app.add_routes([aiohttp.web.get(r"/profile", profile)])  # type: ignore
