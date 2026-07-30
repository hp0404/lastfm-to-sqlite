"""Tests for the CLI, with the HTTP layer replaced by a fake session."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from sqlite_utils import Database

import lastfm.cli
from lastfm.cli import cli
from lastfm.client import LastFM
from tests.conftest import FakeSession, loved_track, page, recent_track


def patch_client(
    monkeypatch: pytest.MonkeyPatch, payloads: list[dict[str, Any]]
) -> None:
    def fake_lastfm(api_key: str) -> LastFM:
        session = FakeSession(payloads)
        return LastFM(api_key, rate_limit=0, session=session)  # type: ignore[arg-type]

    monkeypatch.setattr(lastfm.cli, "LastFM", fake_lastfm)


def test_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "lastfm.db"
    patch_client(
        monkeypatch,
        [
            page("recenttracks", [], total=2),  # scrobble_count
            page(
                "recenttracks",
                [recent_track("Song A", 1000), recent_track("Song B", 900)],
            ),
        ],
    )
    result = CliRunner().invoke(
        cli, ["export", str(db_path), "--api-key", "key", "--user", "hp0404"]
    )

    assert result.exit_code == 0, result.output
    rows = list(Database(db_path)["scrobbles"].rows)
    assert {row["track"] for row in rows} == {"Song A", "Song B"}
    assert Database(db_path).table("scrobbles").pks == ["uts_timestamp"]


def test_export_is_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "lastfm.db"
    payloads = [
        page("recenttracks", [], total=1),
        page("recenttracks", [recent_track("Song A", 1000)]),
    ]
    for _ in range(2):
        patch_client(monkeypatch, payloads)
        result = CliRunner().invoke(
            cli, ["export", str(db_path), "--api-key", "key", "--user", "hp0404"]
        )
        assert result.exit_code == 0, result.output

    assert Database(db_path)["scrobbles"].count == 1


def test_export_reads_env_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "lastfm.db"
    patch_client(
        monkeypatch, [page("recenttracks", [], total=0), page("recenttracks", [])]
    )
    monkeypatch.setenv("LASTFM_API_KEY", "key")
    monkeypatch.setenv("LASTFM_USERNAME", "hp0404")

    result = CliRunner().invoke(cli, ["export", str(db_path)])
    assert result.exit_code == 0, result.output


def test_loved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "lastfm.db"
    patch_client(
        monkeypatch,
        [
            page("lovedtracks", [], total=1),
            page("lovedtracks", [loved_track("My Friend Dario", 1234)]),
        ],
    )
    result = CliRunner().invoke(
        cli, ["loved", str(db_path), "--api-key", "key", "--user", "hp0404"]
    )

    assert result.exit_code == 0, result.output
    rows = list(Database(db_path)["loved_tracks"].rows)
    assert rows[0]["track"] == "My Friend Dario"


def test_missing_api_key_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LASTFM_API_KEY", raising=False)
    result = CliRunner().invoke(
        cli, ["export", str(tmp_path / "x.db"), "--user", "hp0404"]
    )
    assert result.exit_code != 0
    assert "--api-key" in result.output
