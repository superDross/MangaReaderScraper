import os
import re
import subprocess
from unittest import mock

import pytest

from scraper.config import HERE
from scraper.custom_exceptions import VolumeDoesntExist
from tests.utils import mock_requests_get_return

PAGE_URL = "http://mangareader.net/dragon-ball-episode-of-bardock/2/2"


@mock.patch("scraper.download.get_html_from_url")
def test_get_all_volumes_url(mocked_func, manga_title_page_html, download):
    mocked_func.return_value = manga_title_page_html
    results = download._get_all_volume_urls()
    expected = [
        "http://mangareader.net/dragon-ball-episode-of-bardock/1",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2",
        "http://mangareader.net/dragon-ball-episode-of-bardock/3",
    ]
    assert expected == results


def test_get_all_volume_page_urls(download, manga_volume_html):
    results = download._get_all_volume_pages_urls(manga_volume_html)

    expected = [
        "http://mangareader.net/dragon-ball-episode-of-bardock/2",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/2",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/3",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/4",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/5",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/6",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/7",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/8",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/9",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/10",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/11",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/12",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/13",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/14",
        "http://mangareader.net/dragon-ball-episode-of-bardock/2/15",
    ]

    assert results == expected


def test_check_volume_pass(download, manga_volume_html):
    results = download._check_volume_exists(manga_volume_html)
    assert results is None


def test_check_volume_fails(download, manga_bad_volume_html):
    with pytest.raises(VolumeDoesntExist):
        download._check_volume_exists(manga_bad_volume_html)


def test_get_page_filename(download):
    results = download._get_page_filename(PAGE_URL)
    # truncate the result to remove dirs project root & above
    index = re.search("tests", results).start()
    expected = "tests/test_files/jpgs/dragon-ball-episode-of-bardock_2_2.jpg"
    assert results[index:] == expected


@mock.patch("scraper.download.requests.get")
@mock.patch("scraper.download.get_html_from_url")
def test_download_page(mocked_func, mocked_requests, manga_volume_page_html, download):
    mocked_func.return_value = manga_volume_page_html

    requests_return = mock_requests_get_return(b"h")
    mocked_requests.return_value = requests_return
    download.download_page(PAGE_URL)

    filename = download._get_page_filename(PAGE_URL)
    assert os.path.exists(filename)

    filecontents = open(filename, "r").read()
    assert filecontents == "h"


def teardown_module(module):
    files = [f"{HERE}/tests/test_files/jpgs/dragon-ball-episode-of-bardock_2_2.jpg"]
    for f in files:
        os.remove(f)
