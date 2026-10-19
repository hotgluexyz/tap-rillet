"""Authentication helpers for Rillet."""

from hotglue_singer_sdk.authenticators import OAuthAuthenticator


class RilletAuthenticator(OAuthAuthenticator):
    """Expose Rillet's static API key through access-token support."""

    def update_access_token_locally(self) -> None:
        """Copy the static API key into the access-token configuration field."""
        self._tap._config["access_token"] = self._tap._config["api_key"]
