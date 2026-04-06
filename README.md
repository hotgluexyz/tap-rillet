# tap-rillet

A [Singer](https://www.singer.io/) tap that extracts data from **Rillet**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- **REST** HTTP streams against Rillet API **v3** (`client.py` / `streams.py`).
- **Bearer** token authentication (`Authorization: Bearer …`).
- Base URL: **production** `https://api.rillet.com` or **sandbox** `https://sandbox.api.rillet.com` when `sandbox` is true.
- **Pagination**: cursor from `pagination.next_cursor` in the JSON body; passed as the `cursor` query parameter on the next request.
- **Incremental** streams (where applicable): `updated.gt` query parameter, lower bound from Singer state or `start_date` in config; replication key **`updated_at`**.
- Optional **`subsidiary`** config: when set, requests include `subsidiary_id` (used for bills and shared client behavior).

### Streams

| Stream | `path` | Records (JSONPath) | Primary key | Replication key |
| ------ | ------ | ------------------- | ----------- | ----------------- |
| `bills` | `/bills` | `$.bills[*]` | `id` | `updated_at` |
| `vendors` | `/vendors` | `$.vendors[*]` | `id` | `updated_at` |
| `accounts` | `/accounts` | `$.accounts[*]` | `id` | `updated_at` |
| `tax_rates` | `/tax-rates` | `$.tax_rates[*]` | `id` | — (full table) |

### Stream schemas (summary)

Schemas are defined in `tap_rillet/streams.py` (`th.PropertiesList`). Summary of top-level properties:

- **`bills`**: `id`, `vendor_id`, `expense_number`, `items` (line items with `description`, `account_code`, `amount` {`amount`, `currency`}, `fields` {`field_id`, `field_value_id`}, `id`), `bill_date`, `due_date`, `impact_date`, `subsidiary_id`, `external_references`, `exchange_rate` {`base`, `target`, `rate`, `date`}, `status`, `updated_at`.
- **`vendors`**: `id`, `name`, `account_code`, `address` {`line1`, `city`, `state`, `zip_code`, `country`}, `payment_terms`, `external_references` (array of strings), `ten_ninety_nine_eligible`, `fields` {`field_id`, `field_value_id`}, `updated_at`.
- **`accounts`**: `id`, `code`, `name`, `type`, `subtype`, `status`, `intercompany`, `updated_at`.
- **`tax_rates`**: `id`, `country`, `code`, `percentage`, `description`.

If the API returns list keys that differ (for example under `/tax-rates`), adjust `records_jsonpath` on the stream class.

## Requirements

- Python **3.10+** (see `requires-python` in `pyproject.toml`).

## Installation

1. **Clone** this repository and `cd` into the project directory.
2. **Create `config.json`** in the project root with your credentials and settings (see [Configuration](#configuration) for the fields and an example).
3. **Create a virtual environment** and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

4. **Install the package** in editable mode:

```bash
pip install -e .
```

5. **Run the tap** (with the venv still activated):

```bash
tap-rillet --help
```

## Configuration

| Setting | Type | Required | Default | Description |
| ------- | ---- | -------- | ------- | ----------- |
| `api_key` | string | yes | — | Rillet API key (Bearer token). |
| `start_date` | string (datetime) | no | `2000-01-01T00:00:00Z` | Earliest `updated.gt` lower bound when no bookmark exists. |
| `sandbox` | boolean | no | `false` | Use `https://sandbox.api.rillet.com`. |
| `api_version` | string | no | `3` | Sent as `X-Rillet-API-Version`. |
| `subsidiary` | string | no | — | If set, adds `subsidiary_id` to list requests (e.g. bills). |

Run `tap-rillet --about` (or `tap-rillet --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "api_key": "YOUR_API_KEY",
  "start_date": "2000-01-01T00:00:00Z",
  "sandbox": false,
  "api_version": "3",
  "subsidiary": null
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the SDK merges env into config). Env names follow the tap’s setting keys (see `tap-rillet --about`).

## Usage

With your virtual environment **activated** and `config.json` in place:

Discover stream catalog:

```bash
tap-rillet --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
tap-rillet --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
tap-rillet --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
tap-rillet --about
```

## API / documentation

- Rillet API hosts: `https://api.rillet.com` (production), `https://sandbox.api.rillet.com` (sandbox).
- List endpoints use query parameters `updated.gt` (incremental) and `cursor` (pagination) as implemented in `tap_rillet/client.py`.

## License

MIT — see `LICENSE` and `pyproject.toml`.
