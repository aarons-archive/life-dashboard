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
