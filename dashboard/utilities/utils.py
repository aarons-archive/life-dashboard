# Future
from __future__ import annotations

# Standard Library
import datetime as dt
from typing import TYPE_CHECKING

# Packages
import humanize
import pendulum


if TYPE_CHECKING:
    # My stuff
    from typings.common import ImageFormat
    from utilities import objects


def convert_datetime(
    datetime: dt.datetime | pendulum.DateTime,
    /
) -> pendulum.DateTime:

    datetime.replace(microsecond=0)

    if type(datetime) is dt.datetime and datetime.tzinfo == dt.timezone.utc:
        datetime = datetime.replace(tzinfo=None)

    return pendulum.instance(datetime, tz="UTC")


def format_datetime(
    datetime: dt.datetime | pendulum.DateTime,
    /,
    *,
    seconds: bool = False
) -> str:
    return convert_datetime(datetime).format(f"dddd MMMM Do YYYY [at] hh:mm{':ss' if seconds else ''} A")


def format_date(
    date: pendulum.Date,
    /
) -> str:
    return date.format("dddd MMMM Do YYYY")


def format_time(
    time: pendulum.Time,
    /
) -> str:
    return time.format("hh:mm:ss")


def format_difference(
    datetime: dt.datetime | pendulum.DateTime,
    /,
    *,
    suppress: tuple[str] = ('seconds',)
) -> str:

    datetime = convert_datetime(datetime)

    now = pendulum.now(tz=datetime.timezone)
    now.replace(microsecond=0)

    return humanize.precisedelta(now.diff(datetime), format="%0.0f", suppress=suppress)


def format_seconds(
    seconds: float,
    /,
    *,
    friendly: bool = False
) -> str:

    seconds = round(seconds)

    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)

    days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

    if friendly is True:
        return f"{f'{days}d ' if not days == 0 else ''}{f'{hours}h ' if not hours == 0 or not days == 0 else ''}{minutes}m {seconds}s"

    return f"{f'{days:02d}:' if not days == 0 else ''}{f'{hours:02d}:' if not hours == 0 or not days == 0 else ''}{minutes:02d}:{seconds:02d}"


def avatar(
    person: objects.User,
    /,
    *,
    format: ImageFormat | None = None,
    size: int = 512
) -> str:

    return str(person.display_avatar.replace(format=format or ("gif" if person.display_avatar.is_animated() else "png"), size=size))


def banner(
    person: objects.User,
    /,
    *,
    format: ImageFormat | None = None,
    size: int = 512
) -> str | None:

    return str(person.banner.replace(format=format or ("gif" if person.banner.is_animated() else "png"), size=size)) if person.banner else None


def icon(
    guild: objects.Guild,
    /,
    *,
    format: ImageFormat | None = None,
    size: int = 512
) -> str | None:

    return str(guild.icon.replace(format=format or ("gif" if guild.icon.is_animated() else "png"), size=size)) if guild.icon else None
