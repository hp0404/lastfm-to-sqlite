=====
Usage
=====

Before using ``lastfm`` you'll need to get an access token from *last.fm*. See https://www.last.fm/api

Both ``Python`` and ``CLI`` API have the same functionality: they allow you to export user's playlist history to a SQLite database.

The arguments you should familiarize yourself with are ``--user``, ``--start_date`` and ``--end_date``. 


----------
Python API
----------
To use Python API
:: 
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
    
::

This allows you to work with a trimmed response directly. 

    
---------
Click API
---------
To run script as a command-line tool, use CLI functionality that explicitly uses database to store data
::
    lastfm export 244ec3b62b2501514191234eed07c75d lastfm_dump.db --user Way4Music
::

That will use (or create) a SQLite database called `lastfm_dump.db` and a table called `playlist` to export user's entire playlist. 

To scrape specific dates, use ``--start_date`` and ``--end_date``:
:: 
    lastfm export 244ec3b62b2501514191234eed07c75d lastfm_dump.db --user way4music --start_date 2020-10-01 --end_date 2020-10-29
::