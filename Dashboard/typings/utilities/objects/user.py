# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    # Standard Library
    from typing import Optional


__all__ = (
    "UserResponse",
    "UserDict",
)


class UserResponse(TypedDict, total=False):
    id: str
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: Optional[str]
    accent_color: Optional[int]
    locale: str
    verified: bool
    email: Optional[str]
    flags: int
    premium_type: int
    public_flags: int

    fetched_at: Optional[float]


class UserDict(TypedDict):
    id: int
    created_at: str
    created_ago: str
    username: str
    discriminator: str
    avatar: str
    banner: Optional[str]
    accent_color: Optional[str]
    bot: bool
    system: bool
    mfa_enabled: bool
    premium_type: int
    public_flags: dict[str, bool]
    locale: str
