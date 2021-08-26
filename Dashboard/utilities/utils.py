from __future__ import annotations

from typing import Literal, TYPE_CHECKING


if TYPE_CHECKING:
    from utilities import objects


def avatar(
    person: objects.User,
    *,
    format: Literal["webp", "jpeg", "jpg", "png", "gif"] | None = None,
    size: int = 512
) -> str:

    return str(person.avatar.replace(format=format or ("gif" if person.avatar.is_animated() else "png"), size=size))


def icon(
    guild: objects.Guild,
    *,
    format: Literal["webp", "jpeg", "jpg", "png", "gif"] | None = None,
    size: int = 512
) -> str | None:

    return str(guild.icon.replace(format=format or ("gif" if guild.icon.is_animated() else "png"), size=size)) if guild.icon else None
