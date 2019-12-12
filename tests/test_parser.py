from unittest import mock

import pytest
import requests

from scraper.exceptions import MangaDoesNotExist, VolumeDoesntExist
from scraper.parsers import MangaParser, get_search_results


def test_all_volume_numbers(manga_title_page_html):
    with mock.patch("scraper.parsers.get_html_from_url") as mocked_func:
        mocked_func.return_value = manga_title_page_html
        parser = MangaParser("dragon-ball")
        all_vols = parser.all_volume_numbers()
        assert all_vols == [1, 2, 3]


def test_page_urls(volume_html):
    with mock.patch("scraper.parsers.get_html_from_url") as mocked_func:
        mocked_func.return_value = volume_html
        parser = MangaParser("dragon-ball")
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


def test_invalid_volume_parser(invalid_volume_html):
    with mock.patch("scraper.parsers.get_html_from_url") as mocked_func:
        mocked_func.return_value = invalid_volume_html
        parser = MangaParser("dragon-ball")
        with pytest.raises(VolumeDoesntExist):
            parser.page_urls(2000)


@pytest.mark.parametrize("url_suffix,expected_num", [("2/2", 2), ("2", 1)])
def test_page_data(url_suffix, expected_num, page_html):
    with mock.patch("scraper.parsers.get_html_from_url") as mocked_func:
        mocked_func.return_value = page_html
        parser = MangaParser("dragon-ball")
        page_data = parser.page_data(
            f"http://mangareader.net/dragon-ball-episode-of-bardock/{url_suffix}"
        )
        page_num, img_data = page_data
        assert page_num == expected_num
        # ensure it is an JPEG
        assert "JFIF" in str(img_data[:15])


def test_get_search_results(search_html):
    with mock.patch("scraper.parsers.get_html_from_url") as mocked_func:
        mocked_func.return_value = search_html
        results = get_search_results("Dragon Ball")
        titles = [result.find("a").get("href") for result in results]
        expected = [
            "/dragon-ball",
            "/dragon-ball-sd",
            "/dragon-ball-episode-of-bardock",
            "/dragonball-next-gen",
            "/dragon-ball-z-rebirth-of-f",
            "/dragon-ball-super",
        ]
        assert titles == expected


def test_get_search_results_with_invalid_query(caplog, invalid_search_html):
    with mock.patch("scraper.parsers.get_html_from_url") as mocked_func:
        mocked_func.return_value = invalid_search_html
        with pytest.raises(SystemExit):
            get_search_results("gibberish")
            assert caplog.text == "No search results found for gibberish"


@mock.patch("scraper.utils.requests.get")
def test_404_errors(mock_request):
    mock_resp = requests.models.Response()
    mock_resp.status_code = 404
    mock_request.return_value = mock_resp
    parser = MangaParser("blahblahblah")
    with pytest.raises(MangaDoesNotExist):
        parser.all_volume_numbers()
    with pytest.raises(MangaDoesNotExist):
        parser.page_urls(1)
