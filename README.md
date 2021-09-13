# lastfm

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/hp0404/lastfm/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/hp0404/lastfm-to-sqlite/branch/main/graph/badge.svg?token=31KSGMRE8C)](https://codecov.io/gh/hp0404/lastfm-to-sqlite)
[![Documentation Status](https://readthedocs.org/projects/lastfm/badge/?version=latest)](https://lastfm.readthedocs.io/en/latest/?badge=latest)


- Scrape [LAST.FM](https://www.last.fm/) user's playlists to SQLite. 
- Docs: https://lastfm.readthedocs.io/en/latest/

## Usage

    pip install lastfm-to-sqlite

Now run CLI:

    lastfm export 244ec3b62b2501514191234eed07c75d lastfm_dump.db --user Way4Music

That will use (or create) a SQLite database called `lastfm_dump.db` and a table called `playlist` to export user's entire playlist. 

To scrape specific dates, use `--start_date` and `--end_date`:

    lastfm export 244ec3b62b2501514191234eed07c75 lastfm_dump.db --user way4music --start_date 2021-08-21 --end_date 2021-09-01
    
    
Python-based API works like this: 

    from lastfm import LastFM

    # specific date, ommit start_date and end_date to download all tracks
    api = LastFM(
        api="244ec3b62b2501514191234eed07c75d",
        username="way4music",
        start_date="2021-08-21",
        end_date="2021-09-01"
    )
    data = api.fetch()
    song = next(data)
    print(song)
    container = []
    for item in data:
        container.append(item)
