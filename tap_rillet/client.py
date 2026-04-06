"""HTTP API client (REST or GraphQL), including RilletStream base class."""

from __future__ import annotations

from typing import Any, Optional

import pendulum
import requests
from hotglue_singer_sdk.authenticators import BearerTokenAuthenticator
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override


def _format_updated_gt(value: Any) -> str:
    """Format a datetime for Rillet's ``updated.gt`` query parameter (UTC, ``Z`` suffix)."""
    p = pendulum.instance(value).in_timezone("UTC")
    base = p.strftime("%Y-%m-%dT%H:%M:%S")
    if p.microsecond:
        frac = f"{p.microsecond:06d}".rstrip("0")
        return f"{base}.{frac}Z"
    return f"{base}Z"


class RilletStream(RESTStream):
    """Rillet stream class."""

    records_jsonpath = "$[*]"
    next_page_token_jsonpath = "$.pagination.next_cursor"
    subsidiary = None

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        if self.config.get("sandbox", False):
            return "https://sandbox.api.rillet.com"
        return "https://api.rillet.com"

    @override
    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BearerTokenAuthenticator(stream=self, token=self.config["api_key"])

    @override
    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {
            "X-Rillet-API-Version": self.config.get("api_version"),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Optional[Any]:
        """Return cursor for the next page, or None when pagination is finished."""
        token = None
        if self.next_page_token_jsonpath:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            token = next(iter(all_matches), None)
        return token

    @override
    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page cursor.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict[str, Any] = {}
        if next_page_token:
            params["cursor"] = next_page_token
        if self.replication_key:
            start = self.get_starting_time(context)
            if start is not None:
                params["updated.gt"] = _format_updated_gt(start)
        if self.subsidiary:
            params["subsidiary_id"] = self.subsidiary
        return params
