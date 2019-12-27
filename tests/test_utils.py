import shutil
from pathlib import Path
from unittest import mock

import pytest

from scraper.exceptions import CannotExtractChapter
from scraper.utils import (
    CustomAdapter,
    create_base_config,
    extract_chapter_number,
    get_adapter,
    menu_input,
    request_session,
    settings,
)

CHAPTER_PARAMETERS = [
    ("Chapter 1", "1"),
    ("this hwer      \nCHAPTER 99 HERE", "99"),
    ("chapter 00000099", "99"),
    ("chapter .99", "99"),
    ("chapter 99.5", "99"),
    ("chapter 99b", "99"),
]

FAILED_CHAPTER_PARAMETERS = ["story 1", "nothing here", "chapter ahfhh"]


@pytest.mark.parametrize("inval,expected", CHAPTER_PARAMETERS)
def test_extract_chapter_number(inval, expected):
    chapter_number = extract_chapter_number(inval)
    assert chapter_number == expected


@pytest.mark.parametrize("inval", FAILED_CHAPTER_PARAMETERS)
def test_failed_extract_chapter_number(inval):
    with pytest.raises(CannotExtractChapter):
        extract_chapter_number(inval)


def test_case_adapter(caplog, logger):
    adapter = CustomAdapter(
        logger, extra={"manga": "dragon-ball-super-gt-z-heroes", "volume": 1}
    )
    adapter.warning("Test message")
    assert "[dragon-ball-super-gt-z-heroes:1] Test message" in caplog.text


def test_case_adapter_manga_only(caplog, logger):
    adapter = CustomAdapter(logger, extra={"manga": "dragon-ball-super-gt-z-heroes"})
    adapter.warning("Test message")
    assert "[dragon-ball-super-gt-z-heroes] Test message" in caplog.text


def test_get_adapter(caplog, logger):
    adapter = get_adapter(logger, manga="cool-manga", volume=2)
    adapter.warning("Test message")
    assert "[cool-manga:2] Test message" in caplog.text


def test_create_base_config():
    with mock.patch("scraper.utils.Path.home", lambda: Path("/tmp")):
        create_base_config()
        assert Path("/tmp/.config/mangascraper.ini").exists()


def test_settings():
    with mock.patch("scraper.utils.Path.home", lambda: Path("/tmp")):
        create_base_config()
        config = settings()
        assert config["config"]["manga_directory"] == "/tmp/Downloads"
        assert config["config"]["source"] == "mangareader"
        assert config["config"]["filetype"] == "pdf"


def test_settings_creates_base_config():
    with mock.patch("scraper.utils.Path.home", lambda: Path("/tmp")):
        settings()
        assert Path("/tmp/.config/mangascraper.ini").exists()


def test_requests_session():
    req = request_session(max_attempts=34, intervals=0.5)
    assert len(req.adapters) == 2

    http = req.adapters["http://"]
    assert http.max_retries.total == 34
    assert http.max_retries.backoff_factor == 0.5

    https = req.adapters["https://"]
    assert https.max_retries.total == 34
    assert https.max_retries.backoff_factor == 0.5


@pytest.mark.parametrize("inputs", ["q", "Q", "quit", "QUit"])
def test_menu_input_quit(inputs, monkeypatch):
    gen = (x for x in inputs)
    monkeypatch.setattr("builtins.input", lambda x: next(gen))
    with pytest.raises(SystemExit):
        menu_input()


def teardown_module(module):
    """
    Remove directories after every test, if present

    Fixtures only work before a test is executed, hence
    the need for this module teardown.
    """
    directories = ["/tmp/.config/", "/tmp/Downloads/"]
    for directory in directories:
        if Path(directory).exists():
            shutil.rmtree(directory)
