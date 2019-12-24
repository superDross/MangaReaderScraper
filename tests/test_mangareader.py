from unittest import mock

import pytest

from scraper.exceptions import VolumeDoesntExist
from scraper.parsers.mangareader import (
    MangaReader,
    MangaReaderMangaParser,
    MangaReaderSearch,
)
from tests.helpers import METADATA


def test_all_volume_numbers(mangareader_manga_title_page_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_manga_title_page_html
        parser = MangaReaderMangaParser("dragon-ball")
        all_vols = parser.all_volume_numbers()
        assert all_vols == [1, 2, 3]


def test_page_urls(mangareader_volume_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_volume_html
        parser = MangaReaderMangaParser("dragon-ball")
        page_urls = parser.page_urls(1)
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
        assert page_urls == expected


def test_invalid_volume_parser(mangareader_invalid_volume_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_invalid_volume_html
        parser = MangaReaderMangaParser("dragon-ball")
        with pytest.raises(VolumeDoesntExist):
            parser.page_urls(2000)


@pytest.mark.parametrize("url_suffix,expected_num", [("2/2", 2), ("2", 1)])
def test_page_data(url_suffix, expected_num, mangareader_page_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_page_html
        parser = MangaReaderMangaParser("dragon-ball")
        page_data = parser.page_data(
            f"http://mangareader.net/dragon-ball-episode-of-bardock/{url_suffix}"
        )
        page_num, img_data = page_data
        assert page_num == expected_num
        # ensure it is an JPEG
        assert "JFIF" in str(img_data[:15])


def test_get_search_results(mangareader_search_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_search_html
        mangasearch = MangaReaderSearch("Dragon Ball")
        results = mangasearch.search()
        assert METADATA == results


def test_get_search_results_with_invalid_query(caplog, mangareader_invalid_search_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_invalid_search_html
        with pytest.raises(SystemExit):
            mangasearch = MangaReaderSearch("gibbersish")
            mangasearch.search()
            assert caplog.text == "No search results found for gibberish"


def test_mangareader_test_search_parser(mangareader_search_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_search_html
        mr = MangaReader()
        results = mr.search("a query")
        assert METADATA == results
