from unittest import mock

import pytest

from scraper.exceptions import VolumeDoesntExist
from scraper.parsers.mangareader import (
    MangaReader,
    MangaReaderMangaParser,
    MangaReaderSearch,
)
from tests.helpers import METADATA, MockedImgResponse


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
            (
                1,
                "https://i10.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552925.jpg",
            ),
            (
                2,
                "https://i8.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552927.jpg",
            ),
            (
                3,
                "https://i1.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552929.jpg",
            ),
            (
                4,
                "https://i9.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552931.jpg",
            ),
            (
                5,
                "https://i7.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552933.jpg",
            ),
            (
                6,
                "https://i1.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552935.jpg",
            ),
            (
                7,
                "https://i5.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552937.jpg",
            ),
            (
                8,
                "https://i8.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552939.jpg",
            ),
            (
                9,
                "https://i3.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552941.jpg",
            ),
            (
                10,
                "https://i9.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552943.jpg",
            ),
            (
                11,
                "https://i9.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552945.jpg",
            ),
            (
                12,
                "https://i7.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552947.jpg",
            ),
            (
                13,
                "https://i10.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552949.jpg",
            ),
            (
                14,
                "https://i2.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552951.jpg",
            ),
            (
                15,
                "https://i8.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552953.jpg",
            ),
            (
                16,
                "https://i4.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552955.jpg",
            ),
            (
                17,
                "https://i4.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552957.jpg",
            ),
            (
                18,
                "https://i3.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552959.jpg",
            ),
            (
                19,
                "https://i8.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552961.jpg",
            ),
            (
                20,
                "https://i4.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552963.jpg",
            ),
        ]
        assert page_urls == expected


def test_invalid_volume_parser(mangareader_invalid_volume_html):
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_invalid_volume_html
        parser = MangaReaderMangaParser("dragon-ball")
        with pytest.raises(VolumeDoesntExist):
            parser.page_urls(2000)


@mock.patch("scraper.parsers.mangakaka.requests.get")
def test_page_data(mocked_get, mangareader_page_html):
    mocked_get.return_value = MockedImgResponse()
    with mock.patch("scraper.parsers.mangareader.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_page_html
        parser = MangaReaderMangaParser("dragon-ball")
        page_url = (
            20,
            "https://i4.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552963.jpg",
        )
        page_data = parser.page_data(page_url)
        page_num, img_data = page_data
        assert page_num == 20
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
