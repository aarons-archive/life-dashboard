"""
The following code was taken and modified from https://github.com/Rapptz/discord.py/blob/master/discord/errors.py.

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

# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import aiohttp


def _flatten_error_dict(error_dict: dict[str, Any], key: str = "") -> dict[str, str]:

    items: list[tuple[str, str]] = []

    for k, v in error_dict.items():

        new_key = key + "." + k if key else k

        if isinstance(v, dict):
            try:
                _errors: list[dict[str, Any]] = v["_errors"]
            except KeyError:
                items.extend(_flatten_error_dict(v, new_key).items())  # type: ignore
            else:
                items.append((new_key, " ".join(x.get("message", "") for x in _errors)))
        else:
            items.append((new_key, v))

    return dict(items)


class DiscordException(Exception):
    pass


class HTTPException(DiscordException):

    def __init__(self, response: aiohttp.ClientResponse, message: str | dict[str, Any] | None) -> None:

        self.response = response
        self.code: int
        self.text: str

        if isinstance(message, dict):

            self.code = message.get("code", 0)
            base = message.get("message", "")
            errors = message.get("errors")

            if errors:
                errors = _flatten_error_dict(errors)
                helpful = "\n".join("In %s: %s" % t for t in errors.items())
                self.text = base + "\n" + helpful
            else:
                self.text = base

        else:
            self.text = message or ""
            self.code = 0

        fmt = "{0.status} {0.reason} (error code: {1})"
        if len(self.text):
            fmt += ": {2}"

        super().__init__(fmt.format(self.response, self.code, self.text))


class Forbidden(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class DiscordServerError(HTTPException):
    pass
