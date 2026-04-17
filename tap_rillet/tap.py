"""Rillet tap class."""

from __future__ import annotations

from hotglue_singer_sdk import Tap, Stream
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers

from typing_extensions import override

from tap_rillet.streams import (
    AccountsStream,
    BillsStream,
    TaxRatesStream,
    VendorsStream,
)

STREAM_TYPES = [
    BillsStream,
    VendorsStream,
    AccountsStream,
    TaxRatesStream,
]


class TapRillet(Tap):
    """Singer tap for Rillet."""

    name = "tap-rillet"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
            default="2000-01-01T00:00:00Z"
        ),
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The API key to authenticate against Rillet",
        ),
        th.Property(
            "sandbox",
            th.BooleanType,
            description="Use the Rillet sandbox environment",
            default=False,
        ),
        th.Property(
            "api_version",
            th.StringType,
            description="The API version to use",
            default="3",
        ),
        th.Property(
            "subsidiary",
            th.StringType,
            description="The subsidiary to use to sync bills",
            default=None,
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapRillet.cli()
