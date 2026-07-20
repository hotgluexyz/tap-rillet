"""Reusable ``th.ObjectType`` schema fragments shared across tap-rillet streams.

Defined here (rather than inline in ``streams.py``) to keep the stream classes
readable. Ordered so each helper is declared before anything that references it.
"""

from __future__ import annotations

from hotglue_singer_sdk import typing as th

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

_external_reference = th.ObjectType(
    th.Property("type", th.StringType),
    th.Property("id", th.StringType),
    th.Property("url", th.StringType),
)

_billing_scheme = th.ObjectType(
    th.Property("type", th.StringType),
    th.Property("amount", _bill_amount),
    th.Property("units", th.IntegerType),
    th.Property("tiers", th.ArrayType(th.ObjectType())),
)

_price = th.ObjectType(
    th.Property("type", th.StringType),
    th.Property("amount", _bill_amount),
    th.Property("interval_months", th.IntegerType),
    th.Property("billing_scheme", _billing_scheme),
)

_discount = th.ObjectType(
    th.Property("type", th.StringType),
    th.Property("amount_off", th.StringType),
    th.Property("percentage_off", th.NumberType),
)

_item_tax_rate = th.ObjectType(
    th.Property("percentage", th.StringType),
    th.Property("tax_amount", _bill_amount),
    th.Property("country", th.StringType),
    th.Property("type", th.StringType),
    th.Property("description", th.StringType),
)

_usage_commitment = th.ObjectType(
    th.Property("amount", _bill_amount),
    th.Property("revenue_account", th.StringType),
)

_contract_item = th.ObjectType(
    th.Property("id", th.StringType),
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
)

_invoicing = th.ObjectType(
    th.Property("interval", th.StringType),
    th.Property("payment_terms", th.IntegerType),
    th.Property("day", th.IntegerType),
    th.Property("month_day", th.StringType),
)

_usage_configuration = th.ObjectType(
    th.Property(
        "usage_invoicing",
        th.ObjectType(
            th.Property("frequency", th.StringType),
            th.Property("payment_terms", th.IntegerType),
            th.Property("invoice_date", th.StringType),
            th.Property("cycle", th.StringType),
        ),
    ),
    th.Property(
        "minimum_commitment_invoicing",
        th.ObjectType(
            th.Property("frequency", th.StringType),
            th.Property("payment_terms", th.IntegerType),
        ),
    ),
    th.Property("minimum_commitment_cycle", th.StringType),
    th.Property("contract_level_minimum_commitment", _usage_commitment),
)

_customer_address = th.ObjectType(
    th.Property("line1", th.StringType),
    th.Property("line2", th.StringType),
    th.Property("city", th.StringType),
    th.Property("state", th.StringType),
    th.Property("zip_code", th.StringType),
    th.Property("country", th.StringType),
)

_customer_email = th.ObjectType(
    th.Property("email", th.StringType),
    th.Property("type", th.StringType),
)
