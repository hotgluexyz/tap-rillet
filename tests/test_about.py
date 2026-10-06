"""Tests that `--about` advertises the tap's supported streams without credentials."""

from __future__ import annotations

import ast
import subprocess
import sys

from tap_rillet.tap import STREAM_TYPES


def _about_output() -> str:
    """Run `tap-rillet --about` with no config and return stdout."""
    result = subprocess.run(
        [sys.executable, "-m", "tap_rillet", "--about"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_about_lists_every_registered_stream() -> None:
    """`--about` reports exactly the stream names registered in STREAM_TYPES.

    The SDK omits the list entirely when it cannot resolve stream names, rather than
    failing, so an SDK older than the floor in pyproject.toml or a broken
    `static_stream_names` would silently drop it from `--about`.
    """
    output = _about_output()
    lines = [line for line in output.splitlines() if line.startswith("Supported_Streams:")]
    assert lines, f"`--about` reported no supported streams:\n{output}"

    reported = ast.literal_eval(lines[0].split(":", 1)[1].strip())

    assert reported == sorted(stream.name for stream in STREAM_TYPES)
