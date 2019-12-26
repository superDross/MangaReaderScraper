from unittest import mock

import pytest

from scraper.__main__ import cli, get_manga_parser
from scraper.exceptions import MangaDoesNotExist
from tests.helpers import MockedSiteParser

PATAMETERS = [
    (
        ["--manga", "dragonball"],
        {
            "filetype": "pdf",
            "manga": "dragonball",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": None,
            "upload": None,
            "override_name": None,
            "remove": False,
        },
    ),
    (
        ["--manga", "dragonball", "--volumes", "1", "2"],
        {
            "filetype": "pdf",
            "manga": "dragonball",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": [1, 2],
            "upload": None,
            "override_name": None,
            "remove": False,
        },
    ),
    (
        ["--manga", "one-piece", "--volumes", "231", "--filetype", "cbz"],
        {
            "filetype": "cbz",
            "manga": "one-piece",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": [231],
            "upload": None,
            "override_name": None,
            "remove": False,
        },
    ),
    (
        ["--manga", "something", "--output", "/home/me/Downloads"],
        {
            "filetype": "pdf",
            "manga": "something",
            "output": "/home/me/Downloads",
            "search": None,
            "source": "mangareader",
            "volumes": None,
            "upload": None,
            "override_name": None,
            "remove": False,
        },
    ),
    (
        [
            "--manga",
            "something",
            "--volumes",
            "1-5",
            "40",
            "--override_name",
            "dragon_kin",
        ],
        {
            "filetype": "pdf",
            "manga": "something",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": [1, 2, 3, 4, 5, 40],
            "upload": None,
            "override_name": "dragon_kin",
            "remove": False,
        },
    ),
    (
        ["--manga", "something", "--volumes", "1-5", "40"],
        {
            "filetype": "pdf",
            "manga": "something",
            "output": "/tmp",
            "search": None,
            "source": "mangareader",
            "volumes": [1, 2, 3, 4, 5, 40],
            "upload": None,
            "override_name": None,
            "remove": False,
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
            "filetype": "pdf",
            "upload": None,
            "override_name": None,
            "remove": False,
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
            "filetype": "pdf",
            "override_name": None,
            "remove": False,
            "upload": None,
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
            "filetype": "pdf",
            "upload": None,
            "override_name": None,
            "remove": False,
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
            "filetype": "pdf",
            "upload": None,
            "override_name": None,
            "remove": False,
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
            "filetype": "pdf",
            "upload": None,
            "override_name": None,
            "remove": False,
        },
    ),
]


def test_ioerror_remove_upload_args():
    """
    Ensure --remove causes error if --upload arg not present
    """
    with pytest.raises(IOError):
        cli(["--search", "x", "--remove"])


@pytest.mark.parametrize("arguments,expected", PATAMETERS)
@mock.patch("scraper.__main__.download_manga", mock.Mock(return_value=1))
def test_download_via_cli(arguments, expected):
    args = cli(arguments)
    assert args == expected


def test_get_invalid_manga_parser():
    with pytest.raises(ValueError):
        get_manga_parser("nothing")


@pytest.mark.parametrize("arguments,inputs,expected", SEARCH_PARAMETERS)
@mock.patch("scraper.__main__.download_manga", mock.Mock(return_value=1))
def test_search_via_cli(
    arguments, inputs, expected, monkeypatch, mangareader_search_html
):
    with mock.patch("scraper.__main__.get_manga_parser", return_value=MockedSiteParser):
        gen = (x for x in inputs)
        monkeypatch.setattr("builtins.input", lambda x: next(gen))
        args = cli(arguments)
        assert args == expected


def test_search_if_failed_manga_match(monkeypatch, mangareader_search_html):
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
                "filetype": "pdf",
                "upload": None,
                "override_name": "None",
                "remove": False,
            }
            assert args == expected
