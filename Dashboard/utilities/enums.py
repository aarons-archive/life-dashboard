# Future
from __future__ import annotations

# Packages
from discord.enums import Enum


__all__ = (
    "Environment",
)


class Environment(Enum):

    PRODUCTION = 1
    DEVELOPMENT = 2
