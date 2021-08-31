# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    # Standard Library
    from typing import Optional

    # Packages
    from discord.types.guild import GuildFeature


__all__ = (
    "GuildResponse",
    "GuildDict",
    "RelatedGuilds"
)


class GuildResponse(TypedDict, total=False):
    id: str
    name: str
    icon: Optional[str]
    owner: bool
    permissions: str
    features: list[GuildFeature]

    fetched_at: Optional[float]


class GuildDict(TypedDict):
    id: int
    created_at: str
    created_ago: str
    name: str
    icon: Optional[str]
    owner: bool
    permissions: dict[str, bool]  # TODO: Use some kind of TypedDict here.
    features: list[GuildFeature]


class RelatedGuilds(TypedDict):
    mutual_guilds: Optional[list[GuildDict]]
    non_mutual_guilds: Optional[list[GuildDict]]
    guild: Optional[GuildDict]
