from typing import List
from unittest import mock

import pytest

from scraper.__main__ import cli

PATAMETERS = [
    (
        ["--manga", "dragonball"],
        {
            "cbz": False,
            "manga": "dragonball",
            "output": "/tmp",
            "search": None,
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
            "volumes": None,
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
    search_results = search_html.find_all("div", {"class": "mangaresultitem"})
    with mock.patch("scraper.menu.get_search_results") as mocked_func:
        mocked_func.return_value = search_results
        gen = (x for x in inputs)
        monkeypatch.setattr("builtins.input", lambda x: next(gen))
        args = cli(arguments)
        assert args == expected
