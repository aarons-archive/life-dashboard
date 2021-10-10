# Future
from __future__ import annotations

# Standard Library
from typing import TypedDict


__all__ = (
    "TokenResponse",
)


class TokenResponse(TypedDict, total=False):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

    fetched_at: str
