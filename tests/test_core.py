"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import json

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_rillet.tap import TapRillet

SAMPLE_CONFIG = {
    "api_key": "test-api-key",
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
}


@pytest.mark.parametrize(
    "standard_tap_test",
    get_standard_tap_tests(tap_class=TapRillet, config=SAMPLE_CONFIG)[:2],
)
def test_standard_tap_features(standard_tap_test):
    """Run the SDK checks that do not require a live Rillet account."""
    standard_tap_test()


def test_access_token_support_copies_api_key(tmp_path):
    """Access-token support returns Rillet's static API key."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"api_key": "rillet-api-key"}))
    tap = TapRillet(config=config_path)

    assert TapRillet.fetch_access_token(tap) == {"access_token": "rillet-api-key"}

    assert json.loads(config_path.read_text()) == {
        "api_key": "rillet-api-key",
        "start_date": "2000-01-01T00:00:00Z",
        "sandbox": False,
        "api_version": "3",
        "access_token": "rillet-api-key",
    }
