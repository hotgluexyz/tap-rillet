"""Stream type classes for tap-rillet."""

from __future__ import annotations

from typing import Any, Optional

import pendulum
import requests
from hotglue_singer_sdk import typing as th
from typing_extensions import override

from tap_rillet.client import RilletStream

_bill_amount = th.ObjectType(
    th.Property("amount", th.StringType),
    th.Property("currency", th.StringType),
)

_field = th.ObjectType(
    th.Property("field_id", th.StringType),
    th.Property("field_value_id", th.StringType),
)

_field_definition_value = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("name", th.StringType),
    th.Property("deactivated", th.BooleanType),
)

_field_definition_setting = th.ObjectType(
    th.Property("mandatory", th.BooleanType),
    th.Property("display", th.StringType),
)

_field_definition_settings = th.ObjectType(
    th.Property("EXPENSES", _field_definition_setting),
    th.Property("REVENUE", _field_definition_setting),
)

_bill_item = th.ObjectType(
    th.Property("description", th.StringType),
    th.Property("account_code", th.StringType),
    th.Property("amount", _bill_amount),
    th.Property("fields", th.ArrayType(_field)),
    th.Property("id", th.StringType),
)

_bill_exchange_rate = th.ObjectType(
    th.Property("base", th.StringType),
    th.Property("target", th.StringType),
    th.Property("rate", th.StringType),
    th.Property("date", th.StringType),
)

_vendor_address = th.ObjectType(
    th.Property("line1", th.StringType),
    th.Property("city", th.StringType),
    th.Property("state", th.StringType),
    th.Property("zip_code", th.StringType),
    th.Property("country", th.StringType),
)


class BillsStream(RilletStream):
    """Stream for Rillet bills (``/bills``)."""

    name = "bills"
    path = "/bills"
    records_jsonpath = "$.bills[*]"
    primary_keys = ["id"]
    replication_key = "updated_at"
    @property
    def subsidiary(self) -> str:
        return self.config.get("subsidiary")

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Bill identifier"),
        th.Property("vendor_id", th.StringType),
        th.Property("expense_number", th.StringType),
        th.Property("items", th.ArrayType(_bill_item)),
        th.Property("bill_date", th.StringType),
        th.Property("due_date", th.StringType),
        th.Property("impact_date", th.StringType),
        th.Property("subsidiary_id", th.StringType),
        th.Property("external_references", th.ArrayType(th.ObjectType())),
        th.Property("exchange_rate", _bill_exchange_rate),
        th.Property("status", th.StringType),
        th.Property(
            "updated_at",
            th.DateTimeType,
            description="Incremental replication cursor",
        ),
    ).to_dict()


class VendorsStream(RilletStream):
    """Stream for Rillet vendors (``/vendors``)."""

    name = "vendors"
    path = "/vendors"
    records_jsonpath = "$.vendors[*]"
    primary_keys = ["id"]
    replication_key = "updated_at"
    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Vendor identifier"),
        th.Property("name", th.StringType),
        th.Property("account_code", th.StringType),
        th.Property("address", _vendor_address),
        th.Property("payment_terms", th.IntegerType),
        th.Property("external_references", th.ArrayType(th.StringType)),
        th.Property("ten_ninety_nine_eligible", th.BooleanType),
        th.Property("fields", th.ArrayType(_field)),
        th.Property(
            "updated_at",
            th.DateTimeType,
            description="Incremental replication cursor",
        ),
        th.Property("tax_id", th.StringType),
    ).to_dict()


class AccountsStream(RilletStream):
    """Stream for Rillet chart of accounts (``/accounts``)."""

    name = "accounts"
    path = "/accounts"
    records_jsonpath = "$.accounts[*]"
    primary_keys = ["id"]
    replication_key = "updated_at"
    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Account identifier"),
        th.Property("code", th.StringType),
        th.Property("name", th.StringType),
        th.Property("type", th.StringType),
        th.Property("subtype", th.StringType),
        th.Property("status", th.StringType),
        th.Property("intercompany", th.BooleanType),
        th.Property(
            "updated_at",
            th.DateTimeType,
            description="Incremental replication cursor",
        ),
    ).to_dict()


class TaxRatesStream(RilletStream):
    """Stream for Rillet tax rates (``/tax-rates``)."""

    name = "tax_rates"
    path = "/tax-rates"
    records_jsonpath = "$.tax_rates[*]"
    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Tax rate identifier"),
        th.Property("country", th.StringType),
        th.Property("code", th.StringType),
        th.Property("percentage", th.StringType),
        th.Property("description", th.StringType),
    ).to_dict()


class FieldsStream(RilletStream):
    """Stream for Rillet custom fields (``/fields``)."""

    name = "fields"
    path = "/fields"
    records_jsonpath = "$.fields[*]"
    primary_keys = ["id"]
    replication_key = "updated_at"
    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Field identifier"),
        th.Property("name", th.StringType),
        th.Property("values", th.ArrayType(_field_definition_value)),
        th.Property("settings", _field_definition_settings),
        th.Property(
            "updated_at",
            th.DateTimeType,
            description="Incremental replication cursor",
        ),
    ).to_dict()


class SubsidiariesStream(RilletStream):
    "Stream for Rillet subsidiaries"

    name = "subsidiaries"
    path = "/subsidiaries"
    records_jsonpath = "$.subsidiaries[*]"
    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("currency", th.StringType),
        th.Property("timezone", th.StringType),
        th.Property("trade_name", th.StringType),
        th.Property("type", th.StringType),
    ).to_dict()


_related_entity = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("type", th.StringType),
)

_journal_entry_item = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("description", th.StringType),
    th.Property("amount", _bill_amount),
    th.Property("account_id", th.StringType),
    th.Property("account_code", th.StringType),
    th.Property("side", th.StringType),
    th.Property("fields", th.ArrayType(_field)),
)

_report_journal_entry_item = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("description", th.StringType),
    th.Property("local_amount", _bill_amount),
    th.Property("reporting_amount", _bill_amount),
    th.Property("exchange_rate", th.StringType),
    th.Property("account_id", th.StringType),
    th.Property("account_code", th.StringType),
    th.Property("side", th.StringType),
    th.Property("fields", th.ArrayType(_field)),
)


class JournalEntriesStream(RilletStream):
    """Stream for Rillet journal entries (``/journal-entries``)."""

    name = "journal_entries"
    path = "/journal-entries"
    records_jsonpath = "$.journal_entries[*]"
    primary_keys = ["id"]
    replication_key = "updated_at"

    @property
    def subsidiary(self) -> str:
        return self.config.get("subsidiary")

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Journal entry identifier"),
        th.Property("subsidiary_id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("currency", th.StringType),
        th.Property("date", th.StringType, description="Posting date to GL"),
        th.Property("reversal_date", th.StringType),
        th.Property("attachmentUrl", th.StringType),
        th.Property("exchange_rate", _bill_exchange_rate),
        th.Property("related_entity", _related_entity),
        th.Property("items", th.ArrayType(_journal_entry_item)),
        th.Property(
            "updated_at",
            th.DateTimeType,
            description="Incremental replication cursor",
        ),
    ).to_dict()


class ReportsJournalEntriesStream(RilletStream):
    """Stream for Rillet reports journal entries (``/reports/journal-entries``)."""

    name = "reports_journal_entries"
    path = "/reports/journal-entries"
    records_jsonpath = "$.journal_entries[*]"
    primary_keys = ["id"]

    @property
    def subsidiary(self) -> str:
        return self.config.get("subsidiary")

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Journal entry identifier"),
        th.Property("subsidiary_id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("related_entity", _related_entity),
        th.Property("items", th.ArrayType(_report_journal_entry_item)),
        th.Property("date", th.StringType),
        th.Property("reversal_date", th.StringType),
        th.Property("attachmentUrl", th.StringType),
    ).to_dict()


_breakdown_balance = th.ObjectType(
    th.Property("breakdown_id", th.StringType),
    th.Property("amount", _bill_amount),
)

_breakdown_margin = th.ObjectType(
    th.Property("breakdown_id", th.StringType),
    th.Property("value", th.NumberType),
)

_report_account_entry = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("code", th.StringType),
    th.Property("name", th.StringType),
    th.Property("balances", th.ArrayType(_breakdown_balance)),
)

# Nested account groups can recurse; capture the inner level explicitly and
# allow arbitrary further nesting via a permissive ObjectType.
_report_account_group = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("totals", th.ArrayType(_breakdown_balance)),
    th.Property("accounts", th.ArrayType(_report_account_entry)),
    th.Property("groups", th.ArrayType(th.ObjectType())),
)

_report_section = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("totals", th.ArrayType(_breakdown_balance)),
    th.Property("groups", th.ArrayType(_report_account_group)),
    th.Property("accounts", th.ArrayType(_report_account_entry)),
)

_report_summary_line = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("amounts", th.ArrayType(_breakdown_balance)),
    th.Property("margins", th.ArrayType(_breakdown_margin)),
)

_report_breakdown = th.ObjectType(
    th.Property("type", th.StringType),
    th.Property("name", th.StringType),
    th.Property("id", th.StringType),
)


class ReportsIncomeStatementStream(RilletStream):
    """Stream for Rillet income statement report (``/reports/income-statement``).

    The endpoint returns a single report object for a requested date range.
    The stream iterates calendar months from ``start_date`` through today via
    the pagination hooks (each month window acts as the page token) and emits
    one report record per month; each record's ``period`` object carries the
    month's ``from_date``/``to_date``. Month windows are kept out of
    ``partitions`` so state stays a single stream-level entry.
    """

    name = "reports_income_statement"
    path = "/reports/income-statement"
    records_jsonpath = "$"
    primary_keys = ["from_date", "to_date"]
    next_page_token_jsonpath = None  # months are advanced in get_next_page_token

    @property
    def subsidiary(self) -> str:
        return self.config.get("subsidiary")

    def _sync_range(self) -> tuple[Any, Any]:
        """Return the (start, today) date bounds for the monthly iteration."""
        start = pendulum.parse(
            self.config.get("start_date", "2000-01-01")
        ).in_timezone("UTC").date()
        today = pendulum.now("UTC").date()
        return start, today

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Optional[dict]:
        """Advance to the next month window; None once today's month is done."""
        start, today = self._sync_range()
        current_from = (
            pendulum.parse(previous_token["from_date"]).date()
            if previous_token
            else start
        )
        next_month = current_from.start_of("month").add(months=1)
        if next_month > today:
            return None
        return {
            "from_date": next_month.to_date_string(),
            "to_date": min(next_month.end_of("month"), today).to_date_string(),
        }

    schema = th.PropertiesList(
        th.Property(
            "from_date",
            th.StringType,
            description="Report month start; primary key (flattened from period)",
        ),
        th.Property(
            "to_date",
            th.StringType,
            description="Report month end; primary key (flattened from period)",
        ),
        th.Property(
            "period",
            th.ObjectType(
                th.Property("from_date", th.StringType),
                th.Property("to_date", th.StringType),
            ),
        ),
        th.Property("currency", th.StringType),
        th.Property("breakdowns", th.ArrayType(_report_breakdown)),
        th.Property("sections", th.ArrayType(_report_section)),
        th.Property("summaries", th.ArrayType(_report_summary_line)),
    ).to_dict()

    @override
    def post_process(
        self,
        row: dict,
        context: Optional[dict] = None,
    ) -> Optional[dict]:
        """Flatten the report period onto the record so months can be keyed."""
        period = row.get("period") or {}
        row["from_date"] = period.get("from_date")
        row["to_date"] = period.get("to_date")
        return row

    @override
    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Build the month window for the report from the page token."""
        if next_page_token is None:
            # First request: the (possibly partial) month containing start_date.
            start, today = self._sync_range()
            next_page_token = {
                "from_date": start.to_date_string(),
                "to_date": min(start.end_of("month"), today).to_date_string(),
            }
        params: dict[str, Any] = {
            "from_date": next_page_token["from_date"],
            "to_date": next_page_token["to_date"],
        }
        if self.subsidiary:
            params["subsidiary_id"] = self.subsidiary
        return params