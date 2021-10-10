# Future
from __future__ import annotations

# Standard Library
import time
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    # My stuff
    from typings.utilities.objects.token import TokenResponse


class Token:

    def __init__(
        self,
        data: TokenResponse,
        /
    ) -> None:
        self.data = data

        self._access_token: str = data["access_token"]
        self._expires_in: int = data["expires_in"]
        self._refresh_token: str = data["refresh_token"]
        self._scopes: list[str] = data.get("scope", "").split(" ")
        self._token_type: str = data["token_type"]

        self._fetched_at: float = data.get("fetched_at", time.time())

    def __repr__(self) -> str:
        return f"<Token token_type='{self.token_type}' scopes={self.scopes} expires_in={self.expires_in}>"

    #

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def expires_in(self) -> int:
        return self._expires_in

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @property
    def scopes(self) -> list[str]:
        return self._scopes

    @property
    def token_type(self) -> str:
        return self._token_type

    #

    @property
    def fetched_at(self) -> float:
        return self._fetched_at

    def is_expired(self) -> bool:
        return (time.time() - self.fetched_at) > self.expires_in
