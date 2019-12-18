from unittest import mock

import pytest

from scraper.__main__ import cli
from scraper.exceptions import MangaDoesNotExist
from tests.helpers import MockedSiteParser

PATAMETERS = [
    (
        ["--manga", "dragonball"],
        {
            "cbz": False,
            "manga": "dragonball",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": None,
        },
    ),
    (
        ["--manga", "dragonball", "--volumes", "1", "2"],
        {
            "cbz": False,
            "manga": "dragonball",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": [1, 2],
        },
    ),
    (
        ["--manga", "one-piece", "--volumes", "231", "--cbz"],
        {
            "cbz": True,
            "manga": "one-piece",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": [231],
        },
    ),
    (
        ["--manga", "something", "--output", "/home/me/Downloads"],
        {
            "cbz": False,
            "manga": "something",
            "output": "/home/me/Downloads",
            "search": None,
            "source": "mangareader",
            "volumes": None,
        },
    ),
    (
        ["--manga", "something", "--volumes", "1-5", "40"],
        {
            "cbz": False,
            "manga": "something",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": [1, 2, 3, 4, 5, 40],
        },
    ),
]

SEARCH_PARAMETERS = [
    (
        ["--search", "dragon", "ball"],
        ["1", "5"],
        {
            "manga": "dragon-ball",
            "search": ["dragon", "ball"],
            "source": "mangareader",
            "volumes": [5],
            "output": "/tmp",
            "cbz": False,
        },
    ),
    (
        ["--search", "dragonball"],
        ["6", "8 9"],
        {
            "manga": "dragon-ball-super",
            "search": ["dragonball"],
            "source": "mangareader",
            "volumes": [8, 9],
            "output": "/tmp",
            "cbz": False,
        },
    ),
    (
        ["--search", "dragonball"],
        ["2", "6-10"],
        {
            "manga": "dragon-ball-sd",
            "search": ["dragonball"],
            "source": "mangareader",
            "volumes": [6, 7, 8, 9, 10],
            "output": "/tmp",
            "cbz": False,
        },
    ),
    (
        ["--search", "dragonball"],
        ["2", ""],
        {
            "manga": "dragon-ball-sd",
            "search": ["dragonball"],
            "source": "mangareader",
            "volumes": None,
            "output": "/tmp",
            "cbz": False,
        },
    ),
    (
        ["--search", "dragonball"],
        ["2", "6-10 12"],
        {
            "manga": "dragon-ball-sd",
            "search": ["dragonball"],
            "source": "mangareader",
            "volumes": [6, 7, 8, 9, 10, 12],
            "output": "/tmp",
            "cbz": False,
        },
    ),
]


@pytest.mark.parametrize("arguments,expected", PATAMETERS)
@mock.patch("scraper.__main__.download_manga", mock.Mock(return_value=1))
def test_download_via_cli(arguments, expected):
    args = cli(arguments)
    assert args == expected


@pytest.mark.parametrize("arguments,inputs,expected", SEARCH_PARAMETERS)
@mock.patch("scraper.__main__.download_manga", mock.Mock(return_value=1))
def test_search_via_cli(arguments, inputs, expected, monkeypatch, search_html):
    with mock.patch("scraper.__main__.get_manga_parser", return_value=MockedSiteParser):
        gen = (x for x in inputs)
        monkeypatch.setattr("builtins.input", lambda x: next(gen))
        args = cli(arguments)
        assert args == expected


def test_search_if_failed_manga_match(monkeypatch, search_html):
    def fake_downloader(*args, **kwargs):
        """
        Will raise an error, which should trigger the manga_search
        function and recall this function with the parameters parsed
        from mocked manga_search ("search_activated").

        This will help confirm whether the manga_search function was
        called upon a MangaDoesNotExist error.
        """
        if "search activated" in args or "search activated" in kwargs["manga_name"]:
            return True
        raise MangaDoesNotExist("name")

    with mock.patch("scraper.__main__.download_manga", fake_downloader):
        with mock.patch("scraper.__main__.manga_search") as mocked_func:
            # mock manga_search to return values that signifies it was triggered
            mocked_func.return_value = ("search activated", "2")
            args = cli(["--manga", "dragonballzz"])
            expected = {
                "manga": "search activated",
                "search": ["dragonballzz"],
                "source": "mangareader",
                "volumes": [2],
                "output": "/tmp",
                "cbz": False,
            }
            assert args == expected
