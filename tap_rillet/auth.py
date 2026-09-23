"""Rillet authentication."""

from __future__ import annotations

import json

from hotglue_singer_sdk.authenticators import OAuthAuthenticator
from typing_extensions import override


class RilletAuthenticator(OAuthAuthenticator):
    """Authenticator for Rillet API key auth.

    Aliases the ``api_key`` config field as ``access_token`` so the SDK's
    ``fetch_access_token`` flow works without an OAuth token exchange.
    """

    @override
    def update_access_token_locally(self) -> None:
        self._tap._config["access_token"] = self._tap._config["api_key"]
        if self._tap.config_file is not None:
            with open(self._tap.config_file, "w") as outfile:
                json.dump(self._tap._config, outfile, indent=4)
