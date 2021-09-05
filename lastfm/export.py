# -*- coding: utf-8 -*-
import requests
import datetime
from time import sleep

URL = "http://ws.audioscrobbler.com/2.0"
DATE_FORMAT = "%Y-%m-%d"


def convert_to_timestamp(date):
    """ Convert human-readable `date` as either `datetime.date` or `str` to 
        Unix Timestamp. """
    if isinstance(date, datetime.date):
        return int(date.timestamp())
    return int(datetime.datetime.strptime(date, DATE_FORMAT).timestamp())


def get_metadata(page):
    """ Access requests' metadata containing total number of pages. """
    return page["recenttracks"]["@attr"]


def export_page(page):
    """ Scrape specific information regarding each song in a playlist. """
    playlist = page["recenttracks"]["track"]
    for song in playlist:
        date = song.get("date", "")
        yield {
            "artist": song["artist"]["#text"],
            "album": song["album"]["#text"],
            "song": song["name"],
            "uts_timestamp": date["uts"] if date else "",
            "datetime": date["#text"] if date else "",
        }
        

def fetch(session, params, meta):
    """ Fetch each page and export data using `export_page`. """
    next_page, last_page = params["page"], int(meta["totalPages"])
    while next_page <= last_page:
        params["page"] = next_page
        data = session.get(URL, params=params).json()
        yield from export_page(data)
        next_page += 1
        sleep(1)

        
def get_users_recent_tracks(
    user: str, 
    api: str,
    first_page: int = 1, 
    limit_per_page: int = 200,
    extended: int = 0,
    start_date=None,
    end_date=None,
):
    """ Export user's track history given the parametrs. """
    params = {
        "method": "user.getrecenttracks",
        "user": user,
        "api_key": api,
        "page": first_page,
        "limit": limit_per_page,
        "extended": extended,
        "format": "json"
    }
    if start_date is not None:
        params["from"] = convert_to_timestamp(start_date)
    if end_date is not None:
        params["to"] = convert_to_timestamp(end_date)
    
    r = requests.get(URL, params=params)
    r.raise_for_status()
    
    data = r.json()
    meta = get_metadata(data)
    yield from export_page(data)
    
    with requests.Session() as session:
        params["page"] += 1
        yield from fetch(session, params, meta)
    