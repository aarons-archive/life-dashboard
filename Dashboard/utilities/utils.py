from __future__ import annotations

from typing import Literal, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from utilities import objects


def avatar(
    person: objects.User,
    *,
    format: Optional[Literal["webp", "jpeg", "jpg", "png", "gif"]] = None,
    size: int = 1024
) -> str:

    return str(person.avatar.replace(format=format or ("gif" if person.avatar.is_animated() else "png"), size=size))


def icon(
    guild: objects.Guild,
    *,
    format: Optional[Literal["webp", "jpeg", "jpg", "png", "gif"]] = None,
    size: int = 1024
) -> Optional[str]:

    return str(guild.icon.replace(format=format or ("gif" if guild.icon.is_animated() else "png"), size=size)) if guild.icon else None
