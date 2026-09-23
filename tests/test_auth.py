"""Tests for Rillet access token support."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hotglue_singer_sdk.helpers.capabilities import PluginCapabilities

from tap_rillet.auth import RilletAuthenticator
from tap_rillet.tap import TapRillet


def test_access_token_support_returns_rillet_authenticator() -> None:
    authenticator_cls, auth_endpoint = TapRillet.access_token_support()
    assert authenticator_cls is RilletAuthenticator
    assert auth_endpoint is None


def test_tap_capabilities_include_fetch_access_token() -> None:
    assert PluginCapabilities.ALLOWS_FETCH_ACCESS_TOKEN in TapRillet.capabilities


def test_update_access_token_locally_aliases_api_key(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config = {"api_key": "test-api-key"}
    config_path.write_text(json.dumps(config), encoding="utf-8")

    tap = TapRillet(config=str(config_path))
    auth = RilletAuthenticator(stream=tap.streams["bills"], config_file=str(config_path))
    auth.update_access_token_locally()

    assert tap.config["access_token"] == "test-api-key"
    updated = json.loads(config_path.read_text(encoding="utf-8"))
    assert updated["access_token"] == "test-api-key"


def test_fetch_access_token_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"api_key": "cli-test-key"}), encoding="utf-8")

    TapRillet.fetch_access_token(TapRillet(config=str(config_path)))

    output = json.loads(capsys.readouterr().out)
    assert output == {"access_token": "cli-test-key"}

    updated = json.loads(config_path.read_text(encoding="utf-8"))
    assert updated["access_token"] == "cli-test-key"
