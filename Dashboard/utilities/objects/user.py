# Future
from __future__ import annotations

# Standard Library
import json
import time
from typing import TYPE_CHECKING

# Packages
import discord
import pendulum

# My stuff
from utilities import utils


if TYPE_CHECKING:
    # My stuff
    from typings.utilities.objects.user import UserDict, UserResponse

__all__ = (
    "User",
)


class User:

    def __init__(self, data: UserResponse) -> None:
        self.data = data

        self._id: int = int(data["id"])
        self._username: str = data["username"]
        self._discriminator: str = data["discriminator"]
        self._avatar: str | None = data["avatar"]

        self._banner: str | None = data.get("banner")
        self._accent_color: int | None = data.get("accent_color")

        self._bot: bool = data.get("bot", False)
        self._system: bool = data.get("system", False)
        self._mfa_enabled: bool = data.get("mfa_enabled", False)

        self._premium_type: int = data.get("premium_type", 0)
        self._public_flags: int = data.get("public_flags", 0)
        self._locale: str = data.get("locale", "en")

        self._fetched_at: float = data.get("fetched_at", time.time())

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' discriminator={self.discriminator} bot={self.bot}>"

    #

    @property
    def id(self) -> int:
        return self._id

    @property
    def created_at(self) -> pendulum.DateTime:
        return utils.convert_datetime(discord.utils.snowflake_time(self.id))

    @property
    def username(self) -> str:
        return self._username

    @property
    def discriminator(self) -> str:
        return self._discriminator

    @property
    def default_avatar(self) -> discord.Asset:
        return discord.Asset._from_default_avatar(state=None, index=int(self.discriminator) % len(discord.enums.DefaultAvatar))

    @property
    def avatar(self) -> discord.Asset | None:

        if self._avatar is None:
            return None

        return discord.Asset._from_avatar(None, self.id, self._avatar)

    @property
    def display_avatar(self) -> discord.Asset:
        return self.avatar or self.default_avatar

    @property
    def banner(self) -> discord.Asset | None:

        if self._banner is None:
            return None

        return discord.Asset._from_user_banner(None, self.id, self._banner)

    @property
    def accent_colour(self) -> discord.Colour | None:

        if self._accent_color is None:
            return None

        return discord.Colour(self._accent_color)

    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def system(self) -> bool:
        return self._system

    @property
    def mfa_enabled(self) -> bool:
        return self._mfa_enabled

    @property
    def premium_type(self) -> int:
        return self._premium_type

    @property
    def public_flags(self) -> discord.PublicUserFlags:
        return discord.PublicUserFlags._from_value(self._public_flags)

    @property
    def locale(self) -> str:
        return self._locale

    #

    @property
    def fetched_at(self) -> float:
        return self._fetched_at

    def is_expired(self) -> bool:
        return (time.time() - self.fetched_at) > 20

    #

    def to_dict(self) -> UserDict:

        return {
            "id":            self.id,
            "created_at":    utils.format_datetime(self.created_at),
            "created_ago":   utils.format_difference(self.created_at),
            "username":      self.username,
            "discriminator": self.discriminator,
            "avatar":        utils.avatar(self),
            "banner":        utils.banner(self),
            "accent_colour": str(self.accent_colour) if self.accent_colour else None,
            "bot":           self.bot,
            "system":        self.system,
            "mfa_enabled":   self.mfa_enabled,
            "premium_type":  self.premium_type,
            "public_flags":  dict(self.public_flags),
            "locale":        self.locale
        }
