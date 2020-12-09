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
    from lastfm.export import get_users_recent_tracks

    # playlist is a generator containing all tracks for a given date
    playlist = get_users_recent_tracks(
        user="way4music", 
        start_date="2020-10-01",
        end_date="2020-10-29"
    )
::

This allows you to work with a trimmed JSON directly. 

    
---------
Click API
---------
To run script as a command-line tool, use CLI functionality that explicitly uses database to store data
:: 
    lastfm export output.db --user way4music --start_date 2020-10-01 --end_date 2020-10-29
::