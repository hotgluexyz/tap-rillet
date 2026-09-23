"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import json

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_rillet.auth import RilletAccessTokenAuthenticator
from tap_rillet.tap import TapRillet

SAMPLE_CONFIG = {
    "api_key": "test-api-key",
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
}


_STANDARD_TESTS = [
    test
    for test in get_standard_tap_tests(TapRillet, config=SAMPLE_CONFIG)
    if getattr(test, "__name__", "") != "_test_stream_connections"
]


@pytest.mark.parametrize("test_func", _STANDARD_TESTS)
def test_standard(test_func) -> None:
    """Run offline standard SDK checks."""
    test_func()


def test_access_token_support() -> None:
    """Rillet advertises API-key-backed access-token support."""
    authenticator, auth_endpoint = TapRillet.access_token_support()

    assert authenticator is RilletAccessTokenAuthenticator
    assert auth_endpoint is None


def test_fetch_access_token_returns_api_key(tmp_path, capsys) -> None:
    """The access-token command copies and returns the configured API key."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(SAMPLE_CONFIG), encoding="utf-8")
    tap = TapRillet(config=config_file)

    result = TapRillet.fetch_access_token(tap)

    assert result == {"access_token": SAMPLE_CONFIG["api_key"]}
    assert json.loads(capsys.readouterr().out) == result
    assert json.loads(config_file.read_text(encoding="utf-8"))["access_token"] == SAMPLE_CONFIG[
        "api_key"
    ]
