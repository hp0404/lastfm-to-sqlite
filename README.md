# lastfm

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/hp0404/lastfm/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/hp0404/lastfm-to-sqlite/branch/main/graph/badge.svg?token=31KSGMRE8C)](https://codecov.io/gh/hp0404/lastfm-to-sqlite)
[![Documentation Status](https://readthedocs.org/projects/lastfm/badge/?version=latest)](https://lastfm.readthedocs.io/en/latest/?badge=latest)


Scrape [LAST.FM](https://www.last.fm/) user's playlists to SQLite. Docs: https://lastfm.readthedocs.io/en/latest/

## Usage

Add your [LAST.FM api-key](https://www.last.fm/api) to `.env` file:

    LASTFM_API=asd

Now run CLI:

    lastfm export lastfm_dump --user Way4Music

That will use (or create) a SQLite database called `lastfm_dump` and a table called `playlist` to export user's entire playlist. 

To scrape specific dates, use `--start_date` and `--end_date`:

    lastfm export lastfm_dump --user way4music --start_date 2020-10-15 --end_date 2020-10-25



## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd lastfm
    python -m venv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -r requirements.txt

To run the tests:

    pytest
