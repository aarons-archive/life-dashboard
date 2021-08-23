import json
import time
from typing import Any


class Token:

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

        self._access_token: str = data["access_token"]
        self._expires_in: int = data["expires_in"]
        self._refresh_token: str = data["refresh_token"]
        self._scopes: list[str] = data.get("scope", "").split(" ")
        self._token_type: str = data["token_type"]

        self._created_at: float = data.get("created_at", time.time())

    def __repr__(self) -> str:
        return "<dashboard.Token>"

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

    @property
    def created_at(self) -> float:
        return self._created_at

    #

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.expires_in

    def to_json(self) -> str:

        data = self.data
        data["created_at"] = self.created_at

        return json.dumps(data)