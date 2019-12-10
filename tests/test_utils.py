import os
import shutil
from unittest import mock

from scraper.utils import CustomAdapter, create_base_config, get_adapter, settings


def test_case_adapter(caplog, logger):
    adapter = CustomAdapter(
        logger, extra={"manga": "dragon-ball-super-gt-z-heroes", "volume": 1}
    )
    adapter.warning("Test message")
    assert "[Dragon Ball Super Gt Z Heroes:1] Test message" in caplog.text


def test_case_adapter_manga_only(caplog, logger):
    adapter = CustomAdapter(logger, extra={"manga": "dragon-ball-super-gt-z-heroes"})
    adapter.warning("Test message")
    assert "[Dragon Ball Super Gt Z Heroes] Test message" in caplog.text


def test_get_adapter(caplog, logger):
    adapter = get_adapter(logger, manga="cool-manga", volume=2)
    adapter.warning("Test message")
    assert "[Cool Manga:2] Test message" in caplog.text


def test_create_base_config():
    if not os.path.exists("/tmp/.config/"):
        os.mkdir("/tmp/.config")
    with mock.patch("scraper.utils.os.path.expanduser", lambda x: "/tmp"):
        create_base_config()
        assert os.path.exists("/tmp/.config/mangascraper.ini")


def test_settings():
    os.mkdir("/tmp/.config")
    with mock.patch("scraper.utils.os.path.expanduser", lambda x: "/tmp"):
        create_base_config()
        config = settings()
        assert config["manga_directory"] == "/tmp/Downloads"
        assert config["manga_url"] == "http://mangareader.net"


def test_settings_creates_base_config():
    os.mkdir("/tmp/.config")
    with mock.patch("scraper.utils.os.path.expanduser", lambda x: "/tmp"):
        settings()
        assert os.path.exists("/tmp/.config/mangascraper.ini")
