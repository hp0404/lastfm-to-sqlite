# lastfm-to-sqlite

[![Test](https://github.com/hp0404/lastfm-to-sqlite/actions/workflows/test.yml/badge.svg)](https://github.com/hp0404/lastfm-to-sqlite/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/hp0404/lastfm-to-sqlite/blob/main/LICENSE)

Export your [Last.fm](https://www.last.fm/) listening history — scrobbles and
loved tracks — to a SQLite database.

## Installation

```bash
uv tool install lastfm-to-sqlite
# or: pip install lastfm-to-sqlite
```

## Setup

Grab an API key at https://www.last.fm/api/account/create, then either pass it
with `--api-key` or export it once:

```bash
export LASTFM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export LASTFM_USERNAME=hp0404   # optional, saves you typing --user
```

## Usage

Export all scrobbles into `lastfm.db` (table `scrobbles`):

```bash
lastfm export lastfm.db --user hp0404
```

Only a date range:

```bash
lastfm export lastfm.db --user hp0404 --start-date 2021-08-21 --end-date 2021-09-01
```

Loved tracks (table `loved_tracks`):

```bash
lastfm loved lastfm.db --user hp0404
```

Exports are idempotent: rows are upserted by scrobble timestamp, so re-running
the command only adds what's new.

The resulting database plays nicely with [Datasette](https://datasette.io/)
and [sqlite-utils](https://sqlite-utils.datasette.io/):

```bash
sqlite-utils lastfm.db "select artist, count(*) as plays from scrobbles group by artist order by plays desc limit 10"
```

### Schema

`scrobbles`: `uts_timestamp` (primary key), `datetime` (ISO 8601, UTC),
`artist`, `artist_mbid`, `album`, `album_mbid`, `track`, `track_mbid`, `url`.

`loved_tracks`: same minus the album columns; `uts_timestamp` is the moment
the track was loved.

## Python API

```python
from lastfm import LastFM

with LastFM(api_key="...") as client:
    for track in client.recent_tracks("hp0404", start_date="2021-08-21"):
        print(track["datetime"], track["artist"], "-", track["track"])

    for track in client.loved_tracks("hp0404"):
        print(track["artist"], "-", track["track"])
```

Both methods are generators that paginate through the Last.fm API for you,
politely (rate-limited, with retries on transient errors).

## Development

```bash
git clone https://github.com/hp0404/lastfm-to-sqlite
cd lastfm-to-sqlite
uv sync
uv run pytest
uv run ruff check .
uv run mypy .
```
