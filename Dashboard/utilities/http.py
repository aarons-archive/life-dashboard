"""
The following code was taken and modified from https://github.com/Rapptz/discord.py/blob/master/discord/http.py.

The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
import datetime
import json
import weakref
from typing import Any, ClassVar, Literal, Optional, Type, TypeVar
from urllib.parse import quote

import aiohttp
from discord.abc import Snowflake

from utilities import exceptions


BE = TypeVar("BE", bound=BaseException)
MU = TypeVar("MU", bound="MaybeUnlock")


async def json_or_text(response: aiohttp.ClientResponse) -> dict[str, Any] | str:
    text = await response.text(encoding="utf-8")

    try:
        if response.headers["content-type"] == "application/json":
            return json.loads(text)
    except KeyError:
        pass

    return text


class Route:
    BASE: ClassVar[str] = "https://discord.com/api/v8"

    def __init__(
        self,
        method: Literal["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        path: str,
        token: str,
        **parameters
    ):

        self.method = method
        self.path = path

        self.token = token

        url = self.BASE + self.path
        if parameters:
            url = url.format_map({k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url

        self.channel_id: Optional[Snowflake] = parameters.get("channel_id")
        self.guild_id: Optional[Snowflake] = parameters.get("guild_id")

    @property
    def bucket(self) -> str:
        return f"{self.channel_id}:{self.guild_id}:{self.path}"


class MaybeUnlock:

    def __init__(
        self,
        lock: asyncio.Lock
    ) -> None:

        self.lock: asyncio.Lock = lock
        self._unlock: bool = True

    def __enter__(self: MU) -> MU:
        return self

    def defer(self) -> None:
        self._unlock = False

    def __exit__(
        self,
        exc_type: Optional[Type[BE]],
        exc: Optional[BE],
        traceback: Any,
    ) -> None:

        if self._unlock:
            self.lock.release()


class HTTPClient:

    def __init__(
        self,
        session: aiohttp.ClientSession
    ) -> None:

        self.session: aiohttp.ClientSession = session

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        self._locks: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self._global_over: asyncio.Event = asyncio.Event()
        self._global_over.set()

    async def request(
        self,
        route: Route,
        **kwargs
    ) -> Any:

        bucket = route.bucket
        method = route.method
        url = route.url

        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            if bucket is not None:
                self._locks[bucket] = lock

        headers = {
            "Authorization": f"Bearer {route.token}"
        }
        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = json.dumps(kwargs.pop("json"), separators=(",", ":"))

        kwargs["headers"] = headers

        if not self._global_over.is_set():
            await self._global_over.wait()

        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:

            for tries in range(5):

                try:
                    async with self.session.request(method, url, **kwargs) as response:

                        data = await json_or_text(response)

                    remaining = response.headers.get("X-Ratelimit-Remaining")
                    if remaining == "0" and response.status != 429:

                        reset_after: Optional[str] = response.headers.get("X-Ratelimit-Reset-After")

                        if not reset_after:
                            utc = datetime.timezone.utc
                            now = datetime.datetime.now(utc)
                            reset = datetime.datetime.fromtimestamp(float(response.headers["X-Ratelimit-Reset"]), utc)
                            delta = (reset - now).total_seconds()
                        else:
                            delta = float(reset_after)

                        maybe_lock.defer()
                        self.loop.call_later(delta, lock.release)

                    if 300 > response.status >= 200:
                        return data

                    if response.status == 429:

                        if not response.headers.get("Via") or isinstance(data, str):
                            raise exceptions.HTTPException(response, data)

                        retry_after: float = data["retry_after"]

                        is_global = data.get("global", False)
                        if is_global:
                            self._global_over.clear()

                        await asyncio.sleep(retry_after)

                        if is_global:
                            self._global_over.set()

                        continue

                    if response.status in {500, 502, 504}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    if response.status == 403:
                        raise exceptions.Forbidden(response, data)
                    elif response.status == 404:
                        raise exceptions.NotFound(response, data)
                    elif response.status >= 500:
                        raise exceptions.DiscordServerError(response, data)
                    else:
                        raise exceptions.HTTPException(response, data)

                except OSError as e:
                    if tries < 4 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + tries * 2)
                        continue
                    raise

            if response is not None:
                if response.status >= 500:
                    raise exceptions.DiscordServerError(response, data)

                raise exceptions.HTTPException(response, data)

            raise RuntimeError("Unreachable code in HTTP handling")
