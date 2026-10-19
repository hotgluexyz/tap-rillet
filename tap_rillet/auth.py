"""Authentication helpers for Rillet."""

import json

from hotglue_singer_sdk.authenticators import OAuthAuthenticator


class RilletAuthenticator(OAuthAuthenticator):
    """Expose Rillet's static API key through access-token support."""

    def update_access_token_locally(self) -> None:
        """Copy the static API key into the access-token configuration field."""
        self._tap._config["access_token"] = self._tap._config["api_key"]
        if self._config_file is not None:
            with open(self._config_file, "w") as config_file:
                json.dump(self._tap._config, config_file, indent=4)
