# CLI

Both commands share the same conventions: the database file is created if it
does not exist, credentials can come from `LASTFM_API_KEY` /
`LASTFM_USERNAME` environment variables, and rows are upserted by
`uts_timestamp`, so exports are idempotent and incremental.

## `lastfm export`

Export a user's scrobbles (played tracks).

```bash
lastfm export lastfm.db --user hp0404
lastfm export lastfm.db --user hp0404 --start-date 2021-08-21 --end-date 2021-09-01
```

| Option | Default | Description |
| ------ | ------- | ----------- |
| `--api-key` | `$LASTFM_API_KEY` | Last.fm API key |
| `--user` | `$LASTFM_USERNAME` | Last.fm username |
| `--table` | `scrobbles` | Table to write to |
| `--start-date` | – | Only scrobbles on or after this date (`YYYY-MM-DD`, UTC) |
| `--end-date` | – | Only scrobbles on or before this date (`YYYY-MM-DD`, UTC) |

## `lastfm loved`

Export a user's loved tracks. The Last.fm API does not support date filtering
for loved tracks, so this always exports all of them (still idempotent).

```bash
lastfm loved lastfm.db --user hp0404
```

| Option | Default | Description |
| ------ | ------- | ----------- |
| `--api-key` | `$LASTFM_API_KEY` | Last.fm API key |
| `--user` | `$LASTFM_USERNAME` | Last.fm username |
| `--table` | `loved_tracks` | Table to write to |

## Schema

`scrobbles`:

| Column | Type | Notes |
| ------ | ---- | ----- |
| `uts_timestamp` | integer | Primary key, Unix timestamp of the scrobble |
| `datetime` | text | ISO 8601, UTC |
| `artist`, `album`, `track` | text | `album` may be null |
| `artist_mbid`, `album_mbid`, `track_mbid` | text | MusicBrainz ids, null when Last.fm has none |
| `url` | text | Last.fm track page |

`loved_tracks` has the same columns minus `album` / `album_mbid`;
`uts_timestamp` is the moment the track was loved.
