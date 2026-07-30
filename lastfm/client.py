"""Client for the Last.fm web API (https://www.last.fm/api)."""

from __future__ import annotations

import datetime as dt
import time
from collections.abc import Iterator
from types import TracebackType
from typing import Any, Self

import requests
from requests.adapters import HTTPAdapter, Retry

API_URL = "https://ws.audioscrobbler.com/2.0/"
DATE_FORMAT = "%Y-%m-%d"

DateLike = str | dt.date | dt.datetime


class LastFMError(Exception):
    """Raised when the Last.fm API returns an error payload."""


class LastFM:
    """Read-only client for a user's Last.fm listening history.

    Parameters
    ----------
    api_key : str
        Last.fm API key (https://www.last.fm/api/account/create).
    rate_limit : float, optional
        Seconds to sleep between page requests, by default 0.25.
    session : requests.Session, optional
        Pre-configured HTTP session; mainly useful for testing. When
        omitted, a session with retries on transient errors is created.

    Examples
    --------
    >>> with LastFM(api_key="...") as client:
    ...     for track in client.recent_tracks("hp0404"):
    ...         print(track["artist"], "-", track["track"])
    """

    def __init__(
        self,
        api_key: str,
        *,
        rate_limit: float = 0.25,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.session = session or _default_session()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.session.close()

    def recent_tracks(
        self,
        user: str,
        *,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield every scrobble of `user`, newest first.

        Parameters
        ----------
        user : str
            Last.fm username.
        start_date, end_date : str or datetime.date or datetime.datetime, optional
            Restrict the export to a date range. Strings use the
            ``YYYY-MM-DD`` format; dates are interpreted as UTC.

        Yields
        ------
        dict
            One row per scrobble with keys ``uts_timestamp``, ``datetime``,
            ``artist``, ``artist_mbid``, ``album``, ``album_mbid``,
            ``track``, ``track_mbid``, and ``url``. The currently playing
            track (which has no timestamp yet) is skipped.
        """
        params = _date_params(start_date, end_date)
        for track in self._paginate(
            "user.getrecenttracks", "recenttracks", user, params
        ):
            if track.get("@attr", {}).get("nowplaying") == "true":
                continue
            yield _parse_recent_track(track)

    def loved_tracks(self, user: str) -> Iterator[dict[str, Any]]:
        """Yield every track `user` has loved, newest first.

        Parameters
        ----------
        user : str
            Last.fm username.

        Yields
        ------
        dict
            One row per loved track with keys ``uts_timestamp`` (when the
            track was loved), ``datetime``, ``artist``, ``artist_mbid``,
            ``track``, ``track_mbid``, and ``url``.
        """
        for track in self._paginate("user.getlovedtracks", "lovedtracks", user, {}):
            yield _parse_loved_track(track)

    def scrobble_count(
        self,
        user: str,
        *,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
    ) -> int:
        """Return the number of scrobbles `user` has in the date range."""
        params = _date_params(start_date, end_date)
        return self._total("user.getrecenttracks", "recenttracks", user, params)

    def loved_count(self, user: str) -> int:
        """Return the number of tracks `user` has loved."""
        return self._total("user.getlovedtracks", "lovedtracks", user, {})

    def _get(self, method: str, **params: Any) -> dict[str, Any]:
        query = {"method": method, "api_key": self.api_key, "format": "json", **params}
        response = self.session.get(API_URL, params=query, timeout=30)
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        if "error" in payload:
            raise LastFMError(f"{payload['message']} (error {payload['error']})")
        return payload

    def _total(self, method: str, root: str, user: str, params: dict[str, int]) -> int:
        payload = self._get(method, user=user, limit=1, **params)
        return int(payload[root]["@attr"]["total"])

    def _paginate(
        self, method: str, root: str, user: str, params: dict[str, int]
    ) -> Iterator[dict[str, Any]]:
        page, total_pages = 1, 1
        while page <= total_pages:
            payload = self._get(method, user=user, page=page, limit=200, **params)[root]
            total_pages = int(payload["@attr"]["totalPages"])
            tracks = payload.get("track", [])
            # a single-track page is returned as a dict, not a list
            yield from [tracks] if isinstance(tracks, dict) else tracks
            page += 1
            if page <= total_pages:
                time.sleep(self.rate_limit)


def _default_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def _date_params(
    start_date: DateLike | None, end_date: DateLike | None
) -> dict[str, int]:
    params = {}
    if start_date is not None:
        params["from"] = _to_timestamp(start_date)
    if end_date is not None:
        params["to"] = _to_timestamp(end_date)
    return params


def _to_timestamp(value: DateLike) -> int:
    """Convert a ``YYYY-MM-DD`` string, date, or datetime to a UTC Unix timestamp."""
    if isinstance(value, str):
        value = dt.datetime.strptime(value, DATE_FORMAT).replace(tzinfo=dt.UTC)
    elif not isinstance(value, dt.datetime):
        value = dt.datetime(value.year, value.month, value.day, tzinfo=dt.UTC)
    elif value.tzinfo is None:
        value = value.replace(tzinfo=dt.UTC)
    return int(value.timestamp())


def _parse_recent_track(track: dict[str, Any]) -> dict[str, Any]:
    uts = int(track["date"]["uts"])
    return {
        "uts_timestamp": uts,
        "datetime": dt.datetime.fromtimestamp(uts, tz=dt.UTC).isoformat(),
        "artist": track["artist"]["#text"],
        "artist_mbid": track["artist"]["mbid"] or None,
        "album": track["album"]["#text"] or None,
        "album_mbid": track["album"]["mbid"] or None,
        "track": track["name"],
        "track_mbid": track["mbid"] or None,
        "url": track["url"],
    }


def _parse_loved_track(track: dict[str, Any]) -> dict[str, Any]:
    uts = int(track["date"]["uts"])
    return {
        "uts_timestamp": uts,
        "datetime": dt.datetime.fromtimestamp(uts, tz=dt.UTC).isoformat(),
        "artist": track["artist"]["name"],
        "artist_mbid": track["artist"]["mbid"] or None,
        "track": track["name"],
        "track_mbid": track["mbid"] or None,
        "url": track["url"],
    }
