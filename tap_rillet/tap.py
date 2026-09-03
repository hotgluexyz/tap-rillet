"""Rillet tap class."""

from __future__ import annotations

from hotglue_singer_sdk import Tap, Stream
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers
from hotglue_singer_sdk.helpers.capabilities import AlertingLevel
from hotglue_singer_sdk.tap_base import InvalidCredentialsError

from typing_extensions import override

from tap_rillet.streams import (
    AccountsStream,
    BankAccountsStream,
    BillsStream,
    FieldsStream,
    TaxRatesStream,
    VendorsStream,
    SubsidiariesStream,
    JournalEntriesStream,
    ReportsJournalEntriesStream,
    ReportsIncomeStatementStream,
    ContractsStream,
    ContractItemsStream,
    ProductsStream,
    CustomersStream,
)
from tap_rillet.auth import RilletAuthenticator

STREAM_TYPES = [
    BillsStream,
    VendorsStream,
    AccountsStream,
    TaxRatesStream,
    FieldsStream,
    SubsidiariesStream,
    JournalEntriesStream,
    ReportsJournalEntriesStream,
    ReportsIncomeStatementStream,
    ContractsStream,
    ContractItemsStream,
    ProductsStream,
    CustomersStream,
    BankAccountsStream,
]


class TapRillet(Tap):
    """Singer tap for Rillet."""

    name = "tap-rillet"

    alerting_level = AlertingLevel.ERROR
    exception_alerting_level_map = {
        InvalidCredentialsError: AlertingLevel.NONE,
    }

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

    @classmethod
    def access_token_support(cls, connector=None):
        """Return (authenticator_class, auth_endpoint). Use connector.config when connector (tap instance) is provided."""
        authenticator = RilletAuthenticator
        default_url = "https://api.rillet.com/oauth/token"

        if connector is not None and getattr(connector, "config", None) is not None:
            oauth_url = connector.config.get("auth_url") or default_url
        else:
            oauth_url = default_url

        # Ensure the URL ends with /token
        if oauth_url and not oauth_url.endswith("/token"):
            if oauth_url.endswith("/"):
                oauth_url += "token"
            else:
                oauth_url += "/token"

        return authenticator, oauth_url


if __name__ == "__main__":
    TapRillet.cli()
