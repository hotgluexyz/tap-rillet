"""Stream type classes for tap-rillet."""

from __future__ import annotations

from hotglue_singer_sdk import typing as th

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