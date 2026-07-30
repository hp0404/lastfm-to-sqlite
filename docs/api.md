# Python API

```python
from lastfm import LastFM

with LastFM(api_key="...") as client:
    for track in client.recent_tracks("hp0404", start_date="2021-08-21"):
        print(track["datetime"], track["artist"], "-", track["track"])

    for track in client.loved_tracks("hp0404"):
        print(track["artist"], "-", track["track"])
```

Both methods are generators that paginate through the Last.fm API for you,
politely (rate-limited, with retries on transient errors). Tracks come newest
first, which makes client-side filtering cheap — stop iterating once you are
past the date you care about:

```python
loved_2026 = []
for track in client.loved_tracks("hp0404"):
    if track["datetime"] < "2026-01-01":
        break
    loved_2026.append(track)
```

## Reference

::: lastfm.client.LastFM

::: lastfm.client.LastFMError
