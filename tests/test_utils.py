import shutil
from pathlib import Path
from unittest import mock

from scraper.utils import CustomAdapter, create_base_config, get_adapter, settings


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
        assert config["manga_directory"] == "/tmp/Downloads"
        assert config["source"] == "mangareader"


def test_settings_creates_base_config():
    with mock.patch("scraper.utils.Path.home", lambda: Path("/tmp")):
        settings()
        assert Path("/tmp/.config/mangascraper.ini").exists()


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
