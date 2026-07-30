"""Shared test fixtures: canned Last.fm API payloads and a fake HTTP session."""

from __future__ import annotations

from typing import Any


def recent_track(
    name: str,
    uts: int,
    *,
    artist: str = "Lera Lynn",
    album: str = "True Detective",
    nowplaying: bool = False,
) -> dict[str, Any]:
    track: dict[str, Any] = {
        "name": name,
        "mbid": "",
        "url": f"https://www.last.fm/music/{name}",
        "artist": {"#text": artist, "mbid": "artist-mbid"},
        "album": {"#text": album, "mbid": ""},
    }
    if nowplaying:
        track["@attr"] = {"nowplaying": "true"}
    else:
        track["date"] = {"uts": str(uts), "#text": "irrelevant"}
    return track


def loved_track(name: str, uts: int, *, artist: str = "Vitalic") -> dict[str, Any]:
    return {
        "name": name,
        "mbid": "track-mbid",
        "url": f"https://www.last.fm/music/{name}",
        "artist": {"name": artist, "mbid": "artist-mbid"},
        "date": {"uts": str(uts), "#text": "irrelevant"},
    }


def page(
    root: str,
    tracks: list[dict[str, Any]] | dict[str, Any],
    *,
    total_pages: int = 1,
    total: int = 0,
) -> dict[str, Any]:
    return {
        root: {
            "@attr": {
                "totalPages": str(total_pages),
                "total": str(total or len(tracks)),
            },
            "track": tracks,
        }
    }


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict[str, Any]:
        return self._payload


class FakeSession:
    """Stands in for requests.Session, serving queued payloads."""

    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self.payloads = list(payloads)
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, params: dict[str, Any], timeout: int) -> FakeResponse:
        self.calls.append(params)
        return FakeResponse(self.payloads.pop(0))

    def close(self) -> None:
        pass
