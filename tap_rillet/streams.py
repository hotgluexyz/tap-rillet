"""Stream type classes for tap-rillet."""

from __future__ import annotations

from typing import Any, Optional

import pendulum
import requests
from hotglue_singer_sdk import typing as th
from typing_extensions import override

from tap_rillet.client import RilletStream
from tap_rillet.schema_helpers import (
    _bill_amount,
    _bill_exchange_rate,
    _bill_item,
    _contract_item,
    _customer_address,
    _customer_email,
    _discount,
    _external_reference,
    _field,
    _field_definition_settings,
    _field_definition_value,
    _invoicing,
    _item_tax_rate,
    _journal_entry_item,
    _price,
    _related_entity,
    _report_breakdown,
    _report_journal_entry_item,
    _report_section,
    _report_summary_line,
    _usage_commitment,
    _usage_configuration,
    _vendor_address,
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


class ContractsStream(RilletStream):
    """Stream for Rillet contracts (``/contracts``)."""

    name = "contracts"
    path = "/contracts"
    records_jsonpath = "$.contracts[*]"
    primary_keys = ["id"]

    @property
    def subsidiary(self) -> str:
        return self.config.get("subsidiary")

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Contract identifier"),
        th.Property("customer_id", th.StringType),
        th.Property("subsidiary_id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("status", th.StringType),
        th.Property("start_date", th.StringType),
        th.Property("end_date", th.StringType),
        th.Property("close_date", th.StringType),
        th.Property("total_value", _bill_amount),
        th.Property("invoicing", _invoicing),
        th.Property("usage_configuration", _usage_configuration),
        th.Property("items", th.ArrayType(_contract_item)),
        th.Property("exchange_rate", _bill_exchange_rate),
        th.Property("external_references", th.ArrayType(_external_reference)),
    ).to_dict()


class ContractItemsStream(ContractsStream):
    """Stream for Rillet contract line items.

    There is no dedicated list endpoint for contract items; they are embedded
    in each contract's ``items`` array, so this stream reads ``/contracts``
    and flattens the items, attaching the parent ``contract_id``.
    """

    name = "contract_items"
    primary_keys = ["id"]

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Contract item identifier"),
        th.Property("contract_id", th.StringType, description="Parent contract"),
        th.Property("product_id", th.StringType),
        th.Property("price", _price),
        th.Property("quantity", th.StringType),
        th.Property("total_value", _bill_amount),
        th.Property("revenue_pattern", th.StringType),
        th.Property("discount", _discount),
        th.Property("tax_rate", _item_tax_rate),
        th.Property("start_date", th.StringType),
        th.Property("end_date", th.StringType),
        th.Property("status", th.StringType),
        th.Property("amending", th.StringType),
        th.Property("usage_minimum_commitment", _usage_commitment),
        th.Property("external_references", th.ArrayType(_external_reference)),
        th.Property("fields", th.ArrayType(_field)),
    ).to_dict()

    @override
    def parse_response(self, response: requests.Response) -> Any:
        """Flatten ``items`` out of each contract, tagging the contract id."""
        for contract in response.json().get("contracts") or []:
            for item in contract.get("items") or []:
                yield {**item, "contract_id": contract.get("id")}


class ProductsStream(RilletStream):
    """Stream for Rillet products (``/products``)."""

    name = "products"
    path = "/products"
    records_jsonpath = "$.products[*]"
    primary_keys = ["id"]

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Product identifier"),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("status", th.StringType),
        th.Property("price", _price),
        th.Property("revenue_pattern", th.StringType),
        th.Property("include_in_arr_mrr", th.BooleanType),
        th.Property("account_code", th.StringType),
        th.Property("external_references", th.ArrayType(_external_reference)),
    ).to_dict()


class CustomersStream(RilletStream):
    """Stream for Rillet customers (``/customers``)."""

    name = "customers"
    path = "/customers"
    records_jsonpath = "$.customers[*]"
    primary_keys = ["id"]
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Customer identifier"),
        th.Property("name", th.StringType),
        th.Property("name_on_invoice", th.StringType),
        th.Property("address", _customer_address),
        th.Property("shipping_address", _customer_address),
        th.Property("emails", th.ArrayType(_customer_email)),
        th.Property("external_references", th.ArrayType(_external_reference)),
        th.Property("payment_terms", th.IntegerType),
        th.Property("send_invoices_automatically", th.BooleanType),
        th.Property("send_payment_reminders", th.BooleanType),
        th.Property("fields", th.ArrayType(_field)),
        th.Property(
            "updated_at",
            th.DateTimeType,
            description="Incremental replication cursor",
        ),
    ).to_dict()