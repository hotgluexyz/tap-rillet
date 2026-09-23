"""Rillet access-token support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hotglue_singer_sdk.tap_base import InvalidCredentialsError


class RilletAccessTokenAuthenticator:
    """Expose Rillet's API key through the SDK access-token contract."""

    def __init__(
        self,
        stream: Any,
        config_file: str | None = None,
        auth_endpoint: str | None = None,
    ) -> None:
        """Initialize access-token support for the SDK's dummy stream."""
        self._tap = stream._tap
        self.config = stream.config
        self._config_file = config_file

    def is_token_valid(self) -> bool:
        """Force each access-token request to copy the current API key."""
        return False

    def update_access_token_locally(self) -> None:
        """Copy the non-expiring Rillet API key to the access-token field."""
        api_key = self.config.get("api_key")
        if not api_key:
            raise InvalidCredentialsError("`api_key` is required to retrieve an access token.")

        self._tap._config["access_token"] = api_key
        if self._config_file is not None:
            Path(self._config_file).write_text(
                json.dumps(self._tap._config, indent=4),
                encoding="utf-8",
            )
