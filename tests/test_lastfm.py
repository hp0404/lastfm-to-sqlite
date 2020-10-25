import os
import json
import pytest
from datetime import datetime
from lastfm.export import get_metadata, export_page, convert_to_timestamp, DATE_FORMAT


@pytest.fixture
def page():    
    cwd = os.getcwd()
    path = os.path.join(cwd, "tests", "sample_dump.json")
    with open(path, "r", encoding="utf-8") as f:
        page = json.load(f)
    return page


@pytest.fixture
def date():
    return datetime.today().strftime(DATE_FORMAT)

    
def test_get_metadata(page):
    data = get_metadata(page)
    assert isinstance(data, dict)
    assert set(data.keys()) == {"page", "total", "user", "perPage", "totalPages"}
    
    
def test_export_page(page):
    data = [*export_page(page)]
    song = data[0]
    assert isinstance(song, dict)
    assert set(song.keys()) == {"artist", "album", "song", "uts_timestamp", "datetime"}
    assert all(isinstance(v, str) for v in song.values())
    assert song["artist"] == "Lera Lynn"
    
    
def test_convert_to_timestamp(date):
    assert isinstance(date, str)
    assert isinstance(convert_to_timestamp(date), int)
