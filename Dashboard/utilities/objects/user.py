import json
import time
from typing import Any, Optional

import discord
import discord.enums

from utilities import utils


class User:

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

        self._id: int = data["id"]
        self._username: str = data["username"]
        self._avatar: Optional[str] = data["avatar"]
        self._discriminator: str = data["discriminator"]
        self._public_flags: int = data["public_flags"]
        self._flags: int = data["flags"]
        self._banner: Optional[str] = data["banner"]
        self._banner_color: str = data["banner_color"]
        self._accent_color: int = data["accent_color"]
        self._locale: str = data["locale"]
        self._mfa_enabled: bool = data["mfa_enabled"]
        self._premium_type: int = data.get("premium_type", 0)

        self._created_at: float = data.get("created_at", time.time())

    def __repr__(self) -> str:
        return "<dashboard.User>"

    @property
    def id(self) -> int:
        return int(self._id)

    @property
    def username(self) -> str:
        return self._username

    @property
    def avatar(self) -> discord.Asset:

        if self._avatar is None:
            return discord.Asset._from_default_avatar(None, int(self.discriminator) % len(discord.enums.DefaultAvatar))
        else:
            return discord.Asset._from_avatar(None, self.id, self._avatar)

    @property
    def discriminator(self) -> str:
        return self._discriminator

    @property
    def public_flags(self) -> discord.PublicUserFlags:
        return discord.PublicUserFlags._from_value(self._public_flags)

    @property
    def banner(self) -> Optional[discord.Asset]:

        if self._banner is None:
            return None

        return discord.Asset._from_user_banner(None, self.id, self._banner)

    @property
    def accent_color(self) -> discord.Colour:
        return discord.Colour(self._accent_color)

    @property
    def created_at(self) -> float:
        return self._created_at

    #

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > 20

    def to_dict(self) -> dict[str, Any]:

        return {
            "id":            self.id,
            "username":      self.username,
            "avatar":        utils.avatar(self),
            "discriminator": self.discriminator,
        }

    def to_json(self) -> str:

        data = self.data
        data["created_at"] = self.created_at

        return json.dumps(data)
