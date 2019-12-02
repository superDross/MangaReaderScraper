"""
Pytest fixtures
"""

from unittest import mock

import pytest
from bs4 import BeautifulSoup

from scraper.config import HERE
from scraper.download import DownloadManga


def get_html_file(filepath):
    with open(filepath, "r") as f:
        return f.read()


def get_bs4_tree(filepath):
    html_string = get_html_file(filepath)
    html = BeautifulSoup(html_string, features="lxml")
    return html


@pytest.fixture(scope="session", autouse=True)
def mocked_get_html_from_url_return_value():
    """
    Mocks return value from get_html_from_url in Search object
    for every single test; universal mock.patch
    """
    html_path = f"{HERE}/tests/test_files/dragonball_search.html"
    html_string = get_html_file(html_path)
    html = BeautifulSoup(html_string, features="lxml")
    with mock.patch("scraper.search.get_html_from_url") as mocked_func:
        mocked_func.return_value = html
        yield mocked_func


@pytest.fixture
def manga_search():
    """
    Usage in pytest:
      def test_something(manga_search):
          assert len(manga_search) == 6
    """
    html_path = f"{HERE}/tests/test_files/dragonball_search.html"
    html = get_bs4_tree(html_path)
    return html


@pytest.fixture
def manga_title_page_html():
    html_path = f"{HERE}/tests/test_files/dragonball_bardock_page.html"
    html = get_bs4_tree(html_path)
    return html


@pytest.fixture
def manga_volume_html():
    html_path = f"{HERE}/tests/test_files/dragonball_bardock_volume_2.html"
    html = get_bs4_tree(html_path)
    return html


@pytest.fixture
def manga_volume_page_html():
    html_path = f"{HERE}/tests/test_files/dragonball_bardock_volume_2_page.html"
    html = get_bs4_tree(html_path)
    return html


@pytest.fixture
def manga_bad_volume_html():
    html_path = f"{HERE}/tests/test_files/dragonball_bardock_volume_100.html"
    html = get_bs4_tree(html_path)
    return html


@pytest.fixture
def download():
    download = DownloadManga("dragon-ball-episode-of-bardock")
    download.volume = 2
    return download
