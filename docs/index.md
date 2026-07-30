# lastfm-to-sqlite

Export your [Last.fm](https://www.last.fm/) listening history — scrobbles and
loved tracks — to a SQLite database.

## Installation

```bash
uv tool install lastfm-to-sqlite
# or: pip install lastfm-to-sqlite
```

## Setup

Grab an API key at <https://www.last.fm/api/account/create>, then either pass
it with `--api-key` or export it once:

```bash
export LASTFM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export LASTFM_USERNAME=hp0404   # optional, saves you typing --user
```

## Quickstart

```bash
lastfm export lastfm.db --user hp0404          # all scrobbles
lastfm loved lastfm.db --user hp0404           # loved tracks
```

Exports are idempotent: rows are upserted by scrobble timestamp, so re-running
the command only adds what's new.

The resulting database plays nicely with [Datasette](https://datasette.io/)
and [sqlite-utils](https://sqlite-utils.datasette.io/):

```bash
sqlite-utils lastfm.db "select artist, count(*) as plays from scrobbles group by artist order by plays desc limit 10"
```

See [CLI](cli.md) for all options and the table schema, and
[Python API](api.md) for using the library from code.
