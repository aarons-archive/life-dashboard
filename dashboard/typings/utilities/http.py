# Future
from __future__ import annotations

# Standard Library
from typing import Literal


HTTPMethod = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]

Path = Literal[
    "/users/@me",
    "/users/@me/guilds",
]
