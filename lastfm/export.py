import os
import requests
import datetime
from time import sleep
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())
URL = "http://ws.audioscrobbler.com/2.0"
API = os.environ.get("LASTFM_API")
DATE_FORMAT = "%Y-%m-%d"


def convert_to_timestamp(date):
    if isinstance(date, datetime.date):
        return int(date.timestamp())
    else:
        return int(datetime.datetime.strptime(date, DATE_FORMAT).timestamp())


def get_metadata(page):
    return page["recenttracks"]["@attr"]


def export_page(page):
    playlist = page["recenttracks"]["track"]
    for song in playlist:
        yield {
            "artist": song["artist"]["#text"],
            "album": song["album"]["#text"],
            "song": song["name"],
            "uts_timestamp": song["date"]["uts"],
            "datetime": song["date"]["#text"]
        }
        

def fetch(session, params, meta):
    next_page, last_page = params["page"], int(meta["totalPages"])
    while next_page <= last_page:
        params["page"] = next_page
        data = session.get(URL, params=params).json()
        yield from export_page(data)
        next_page += 1
        sleep(1)

        
def get_users_recent_tracks(
    user: str, 
    first_page: int = 1, 
    limit_per_page: int = 200,
    extended: int = 0,
    start_date=None,
    end_date=None
):
    params = {
        "method": "user.getrecenttracks",
        "user": user,
        "api_key": API,
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
    meta = get_metadata(r.json())
    
    with requests.Session() as session:
        yield from fetch(session, params, meta)
    