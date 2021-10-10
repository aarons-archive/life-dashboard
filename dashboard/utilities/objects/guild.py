# Future
from __future__ import annotations

# Standard Library
import time
from typing import TYPE_CHECKING

# Packages
import discord
import pendulum

# My stuff
from utilities import utils


if TYPE_CHECKING:
    # Packages
    from discord.types.guild import GuildFeature

    # My stuff
    from typings.utilities.objects.guild import GuildDict, GuildResponse


__all__ = (
    "Guild",
)


class Guild:

    def __init__(
        self,
        data: GuildResponse,
        /
    ) -> None:
        self.data = data

        self._id: int = int(data["id"])
        self._name: str = data["name"]
        self._icon: str | None = data["icon"]
        self._owner: bool = data["owner"]
        self._permissions: str = data["permissions"]
        self._features: list[GuildFeature] = data["features"]

        self._fetched_at: float = data.get("fetched_at", time.time())

    def __repr__(self) -> str:
        return f"<Guild id={self.id} name='{self.name}'>"

    #

    @property
    def id(self) -> int:
        return self._id

    @property
    def created_at(self) -> pendulum.DateTime:
        return utils.convert_datetime(discord.utils.snowflake_time(self.id))

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> discord.Asset | None:

        if self._icon is None:
            return None

        return discord.Asset._from_guild_icon(None, self.id, self._icon)

    @property
    def owner(self) -> bool:
        return self._owner

    @property
    def permissions(self) -> discord.Permissions:
        return discord.Permissions(int(self._permissions))

    @property
    def features(self) -> list[GuildFeature]:
        return self._features

    #

    @property
    def fetched_at(self) -> float:
        return self._fetched_at

    def is_expired(self) -> bool:
        return (time.time() - self.fetched_at) > 20

    #

    def to_dict(self) -> GuildDict:

        return {
            "id":          self.id,
            "created_at":  utils.format_datetime(self.created_at),
            "created_ago": utils.format_difference(self.created_at),
            "name":        self.name,
            "icon":        utils.icon(self),
            "owner":       self.owner,
            "permissions": dict(self.permissions),
            "features":    self.features
        }
