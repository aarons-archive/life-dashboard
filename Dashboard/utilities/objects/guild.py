import json
import time
from typing import Any, Optional

import discord
import discord.enums

from utilities import utils


class Guild:

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

        self._id: int = data["id"]
        self._name: str = data["name"]
        self._icon: Optional[str] = data["icon"]
        self._owner: bool = data["owner"]
        self._permissions: str = data["permissions"]
        self._features: list[str] = data["features"]

        self._created_at: int = data.get("created_at")

    def __repr__(self) -> str:
        return "<dashboard.Guild>"

    @property
    def id(self) -> int:
        return int(self._id)

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> Optional[discord.Asset]:

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
    def features(self) -> list[str]:
        return self._features

    @property
    def created_at(self) -> float:
        return self._created_at or time.time()

    #

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > 20

    def to_dict(self) -> dict[str, Any]:

        return {
            "id": self.id,
            "name": self.name,
            "icon": utils.icon(self),
            "owner": self.owner,
            "permissions": dict(self.permissions),
            "features": self.features
        }

    def to_json(self) -> str:

        data = self.data
        data["created_at"] = self.created_at

        return json.dumps(data)
