import os
import json
import pytest
import datetime
from lastfm import LastFM

@pytest.fixture
def page():    
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", "sample_dump.json")
    with open(path, "r", encoding="utf-8") as f:
        page = json.load(f)
    return page

@pytest.fixture
def date():
    return datetime.datetime.today().strftime(LastFM.DATE_FORMAT)

@pytest.fixture
def apikey():
    return "342ec3b62b2501514199059eed07c75a"

@pytest.fixture
def api(apikey, date):
    return LastFM(api=apikey, username="way4Music", start_date=date)

def test_convert_to_timestamp(api):
    assert isinstance(api.start_date, (str, datetime.date))
    assert isinstance(api._convert_to_timestamp(api.start_date), int)

def test_ensure_context_created(api):
    api.context_created = True
    assert api.ensure_context_created() == None

def test_process_response(page):
    data = LastFM.process_response(page)
    song = next(data)
    assert isinstance(song, dict)
    assert set(song.keys()) == {"artist", "album", "song", "uts_timestamp", "datetime"}
    assert song["artist"] == "Lera Lynn"
