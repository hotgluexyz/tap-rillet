"""HTTP API client (REST or GraphQL), including RilletStream base class."""

from __future__ import annotations

from typing import Any, Callable, Generator, Optional

import backoff
import pendulum
import requests
from hotglue_singer_sdk.authenticators import BearerTokenAuthenticator
from hotglue_singer_sdk.helpers._network import giveup_oserror_not_transient_network
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import RESTStream
from hotglue_singer_sdk.tap_base import InvalidCredentialsError
from hotglue_singer_sdk.exceptions import RetriableAPIError
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
    # Max page size allowed by the API (default is 25); fewer requests per sync
    # keeps us under the rate limit.
    page_size = 100

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
    def validate_response(self, response: requests.Response) -> None:
        if response.status_code == 401:
            raise InvalidCredentialsError(self.response_error_message(response))
        elif response.status_code == 429:
            raise requests.exceptions.RetryError(
                self.response_error_message(response)
            )
        elif (
            response.status_code in self.extra_retry_statuses
            or 500 <= response.status_code < 600
        ):
            raise RetriableAPIError(self.response_error_message(response), response)
        else:
            super().validate_response(response)

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
        if self.page_size:
            params["limit"] = self.page_size
        if next_page_token:
            params["cursor"] = next_page_token
        if self.replication_key:
            start = self.get_starting_time(context)
            if start is not None:
                params["updated.gt"] = _format_updated_gt(start)
        if self.subsidiary:
            params["subsidiary_id"] = self.subsidiary
        return params

    @override
    def backoff_wait_generator(self) -> Callable[..., Generator[int, Any, None]]:
        """Return a wait generator sized for Rillet's rate limit.

        Rillet allows 60 requests per rolling one-minute window and returns a
        bare 429 with no ``Retry-After`` or ``X-RateLimit-*`` headers, so the
        retry schedule must be able to out-wait the full window. The SDK
        default (``expo(factor=2)``, 5 tries, ~30s total) cannot.
        """
        return backoff.expo(factor=5, max_value=60)

    @override
    def backoff_max_tries(self) -> int:
        """Allow enough attempts for the waits to span the one-minute window."""
        return 8

    @override
    def request_decorator(self, func: Callable) -> Callable:
        """Decorate the request method with retry behaviour.

        Same wiring as the SDK default, but with ``jitter=None``: the default
        full jitter draws each wait from ``uniform(0, value)``, which can
        shrink the whole retry schedule below Rillet's one-minute rate-limit
        window. Deterministic waits (5, 10, 20, 40, 60, 60, 60s) guarantee the
        window clears before we give up.
        """
        return backoff.on_exception(
            self.backoff_wait_generator,
            self.backoff_exceptions(),
            max_tries=self.backoff_max_tries,
            on_backoff=self.backoff_handler,
            giveup=giveup_oserror_not_transient_network,
            jitter=None,
        )(func)
