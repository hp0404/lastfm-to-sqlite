"""Tests for lastfm.client against a fake HTTP session (no network)."""

from __future__ import annotations

import datetime as dt
from typing import Any

import pytest

from lastfm.client import LastFM, LastFMError, _to_timestamp
from tests.conftest import FakeSession, loved_track, page, recent_track


def make_client(payloads: list[dict[str, Any]]) -> tuple[LastFM, FakeSession]:
    session = FakeSession(payloads)
    client = LastFM("key", rate_limit=0, session=session)  # type: ignore[arg-type]
    return client, session


def test_recent_tracks_paginates_and_parses() -> None:
    client, session = make_client(
        [
            page("recenttracks", [recent_track("Song A", 1000)], total_pages=2),
            page("recenttracks", [recent_track("Song B", 900)], total_pages=2),
        ]
    )
    rows = list(client.recent_tracks("hp0404"))

    assert [row["track"] for row in rows] == ["Song A", "Song B"]
    assert rows[0] == {
        "uts_timestamp": 1000,
        "datetime": "1970-01-01T00:16:40+00:00",
        "artist": "Lera Lynn",
        "artist_mbid": "artist-mbid",
        "album": "True Detective",
        "album_mbid": None,
        "track": "Song A",
        "track_mbid": None,
        "url": "https://www.last.fm/music/Song A",
    }
    assert [call["page"] for call in session.calls] == [1, 2]
    assert session.calls[0]["limit"] == 200


def test_recent_tracks_passes_date_range() -> None:
    client, session = make_client([page("recenttracks", [])])
    list(client.recent_tracks("hp0404", start_date="2021-08-21", end_date="2021-09-01"))

    assert session.calls[0]["from"] == 1629504000
    assert session.calls[0]["to"] == 1630454400


def test_recent_tracks_skips_nowplaying() -> None:
    client, _ = make_client(
        [
            page(
                "recenttracks",
                [
                    recent_track("Playing now", 0, nowplaying=True),
                    recent_track("Done", 500),
                ],
            )
        ]
    )
    rows = list(client.recent_tracks("hp0404"))
    assert [row["track"] for row in rows] == ["Done"]


def test_single_track_page_is_not_a_list() -> None:
    client, _ = make_client([page("recenttracks", recent_track("Only one", 42))])
    rows = list(client.recent_tracks("hp0404"))
    assert [row["track"] for row in rows] == ["Only one"]


def test_loved_tracks() -> None:
    client, _ = make_client(
        [page("lovedtracks", [loved_track("My Friend Dario", 1234)])]
    )
    rows = list(client.loved_tracks("hp0404"))
    assert rows == [
        {
            "uts_timestamp": 1234,
            "datetime": "1970-01-01T00:20:34+00:00",
            "artist": "Vitalic",
            "artist_mbid": "artist-mbid",
            "track": "My Friend Dario",
            "track_mbid": "track-mbid",
            "url": "https://www.last.fm/music/My Friend Dario",
        }
    ]


def test_counts() -> None:
    client, session = make_client(
        [
            page("recenttracks", [], total=208463),
            page("lovedtracks", [], total=17),
        ]
    )
    assert client.scrobble_count("hp0404") == 208463
    assert client.loved_count("hp0404") == 17
    assert all(call["limit"] == 1 for call in session.calls)


def test_api_error_raises() -> None:
    client, _ = make_client([{"error": 6, "message": "User not found"}])
    with pytest.raises(LastFMError, match="User not found"):
        list(client.recent_tracks("nobody"))


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2021-08-21", 1629504000),
        (dt.date(2021, 8, 21), 1629504000),
        (dt.datetime(2021, 8, 21, 12, 30, tzinfo=dt.UTC), 1629549000),
        (dt.datetime(2021, 8, 21, 12, 30), 1629549000),  # noqa: DTZ001 - naive input on purpose
    ],
)
def test_to_timestamp(value: str | dt.date | dt.datetime, expected: int) -> None:
    assert _to_timestamp(value) == expected
