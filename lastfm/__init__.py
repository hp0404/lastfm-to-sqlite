# -*- coding: utf-8 -*-
import datetime
import requests
from time import sleep
from typing import Dict, Iterable, List, Union


Song = Dict[str, Union[str, int]]


class APIError(Exception):
    pass


class LastFM:

    URL = "http://ws.audioscrobbler.com/2.0"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self,
        api: str,
        username: str,
        first_page: int = 1,
        limit_per_page: int = 200,
        extended: int = 0,
        start_date=None,
        end_date=None,
    ):
        self.api = self._validate_apikey(api)
        self.username = username
        self.first_page = first_page
        self.limit_per_page = limit_per_page
        self.extended = extended
        self.start_date = start_date
        self.end_date = end_date

        self.context_created = False
        self.session = None
        self.total_pages = None

    def __del__(self) -> None:
        if self.session:
            self.session.close()

    @staticmethod
    def _validate_apikey(api: str) -> str:
        if api.isalnum() and len(api) == 32:
            return api
        raise APIError("API key should be 32 alphanum char. long.")

    @staticmethod
    def _convert_to_timestamp(date: Union[str, datetime.date]) -> int:
        if isinstance(date, datetime.date):
            return int(date.timestamp())
        return int(datetime.datetime.strptime(date, LastFM.DATE_FORMAT).timestamp())

    @staticmethod
    def process_response(page: List[Song]) -> Iterable[Song]:
        playlist = page["recenttracks"]["track"]
        for song in playlist:
            date = song.get("date", "")
            yield {
                "artist": song["artist"]["#text"],
                "album": song["album"]["#text"],
                "song": song["name"],
                "uts_timestamp": int(date["uts"]) if date else "",
                "datetime": date["#text"] if date else "",
            }

    def ensure_context_created(self) -> None:
        if self.context_created:
            return
        self.session = requests.Session()

    def fetch(self) -> Iterable[Song]:
        while self.params["page"] <= self.total_pages:
            response = self.session.get(LastFM.URL, params=self.params).json()
            yield from self.process_response(response)
            self.params["page"] += 1
            sleep(1)

    def get_users_recent_tracks(self) -> Iterable[Song]:
        self.ensure_context_created()
        self.params = {
            "method": "user.getrecenttracks",
            "user": self.username,
            "api_key": self.api,
            "page": self.first_page,
            "limit": self.limit_per_page,
            "extended": self.extended,
            "format": "json",
        }
        if self.start_date is not None:
            self.params["from"] = self._convert_to_timestamp(self.start_date)
        if self.end_date is not None:
            self.params["to"] = self._convert_to_timestamp(self.end_date)
        response = self.session.get(LastFM.URL, params=self.params).json()
        self.total_pages = int(response["recenttracks"]["@attr"]["totalPages"])
        yield from self.fetch()
