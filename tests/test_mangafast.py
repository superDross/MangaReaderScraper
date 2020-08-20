from unittest import mock

import pytest

from scraper.exceptions import VolumeDoesntExist
from scraper.parsers.mangafast import MangaFast, MangaFastMangaParser, MangaFastSearch
from tests.helpers import MockedImgResponse


def test_all_volume_numbers(mangafast_manga_title_page_html):
    with mock.patch("scraper.parsers.mangafast.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangafast_manga_title_page_html
        parser = MangaFastMangaParser("dragon-ball-super")
        all_vols = parser.all_volume_numbers()
        expected = [
            62,
            61,
            60,
            59,
            58,
            57,
            56,
            55,
            54,
            53,
            52,
            51,
            50,
            49,
            48,
            47,
            46,
            45,
            44,
            43,
            42,
            41,
            40,
            39,
            38,
            37,
            36,
            35,
            34,
            33,
            32,
            31,
            30,
            29,
            28,
            27,
            26,
            25,
            24,
            23,
            22,
            21,
            20,
            19,
            18,
            17,
            16,
            15,
            14,
            13,
            12,
            11,
            10,
            9,
            8,
            7,
            6,
            5,
            4,
            2,
            1,
        ]
        assert all_vols == expected


def test_page_urls(mangafast_volume_html):
    func = "scraper.parsers.mangafast.get_html_from_url"
    method = "scraper.parsers.mangafast.MangaFastMangaParser.all_volume_numbers"

    with mock.patch(func) as mocked_func:
        mocked_func.return_value = mangafast_volume_html

        with mock.patch(method) as mocked_method:
            mocked_method.return_value = [62, 61, 2, 1]

            parser = MangaFastMangaParser("dragon-ball-super")
            page_urls = parser.page_urls(1)
            expected = [
                (
                    1,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-1.jpg?q=70",
                ),
                (
                    2,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-2.jpg?q=70",
                ),
                (
                    3,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-3.jpg?q=70",
                ),
                (
                    4,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-4.jpg?q=70",
                ),
                (
                    5,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-5.jpg?q=70",
                ),
                (
                    6,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-6.jpg?q=70",
                ),
                (
                    7,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-7.jpg?q=70",
                ),
                (
                    8,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-8.jpg?q=70",
                ),
                (
                    9,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-9.jpg?q=70",
                ),
                (
                    10,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-10.jpg?q=70",
                ),
                (
                    11,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-11.jpg?q=70",
                ),
                (
                    12,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-12.jpg?q=70",
                ),
                (
                    13,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-13.jpg?q=70",
                ),
                (
                    14,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-14.jpg?q=70",
                ),
                (
                    15,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-15.jpg?q=70",
                ),
                (
                    16,
                    "https://i0.wp.com/mangafast.net/img4/2020-07-22/576980/dragon-ball-super-chapter-1-page-16.jpg?q=70",
                ),
            ]
            assert page_urls == expected


def test_invalid_volume_parser(mangafast_volume_html):
    func = "scraper.parsers.mangafast.get_html_from_url"
    method = "scraper.parsers.mangafast.MangaFastMangaParser.all_volume_numbers"

    with mock.patch(func) as mocked_func:
        mocked_func.return_value = mangafast_volume_html

        with mock.patch(method) as mocked_method:
            mocked_method.return_value = [62, 61, 2, 1]

            parser = MangaFastMangaParser("dragon-ball-super")
            with pytest.raises(VolumeDoesntExist):
                parser.page_urls(2000)


@mock.patch("scraper.parsers.mangareader.requests.get")
def test_page_data(mocked_get, mangareader_page_html):
    mocked_get.return_value = MockedImgResponse()
    with mock.patch("scraper.parsers.mangafast.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangareader_page_html
        parser = MangaFastMangaParser("dragon-ball")
        page_url = (
            20,
            "https://i4.imggur.net/dragon-ball-episode-of-bardock/1/dragon-ball-episode-of-bardock-2552963.jpg",
        )
        page_data = parser.page_data(page_url)
        page_num, img_data = page_data
        assert page_num == 20
        # ensure it is an JPEG
        assert "JFIF" in str(img_data[:15])


def test_get_search_results(mangafast_search_html):
    expected = {
        "1": {
            "chapters": "17",
            "manga_url": "super-dragon-ball-heroes-dark-demon-realm-mission",
            "source": "mangafast",
            "title": "Super Dragon Ball Heroes: Dark Demon Realm Mission!",
        },
        "2": {
            "chapters": "62",
            "manga_url": "dragon-ball-super",
            "source": "mangafast",
            "title": "Dragon Ball Super",
        },
    }

    with mock.patch("scraper.parsers.base.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangafast_search_html
        mangasearch = MangaFastSearch("Dragon Ball Super")
        results = mangasearch.search()
        assert expected == results


def test_get_search_results_with_invalid_query(caplog, mangafast_invalid_search_html):
    with mock.patch("scraper.parsers.base.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangafast_invalid_search_html
        with pytest.raises(SystemExit):
            mangasearch = MangaFastSearch("gibbersish")
            mangasearch.search()
            assert caplog.text == "No search results found for gibberish"


def test_mangafast_search_parser(mangafast_search_html):
    expected = {
        "1": {
            "chapters": "17",
            "manga_url": "super-dragon-ball-heroes-dark-demon-realm-mission",
            "source": "mangafast",
            "title": "Super Dragon Ball Heroes: Dark Demon Realm Mission!",
        },
        "2": {
            "chapters": "62",
            "manga_url": "dragon-ball-super",
            "source": "mangafast",
            "title": "Dragon Ball Super",
        },
    }

    with mock.patch("scraper.parsers.base.get_html_from_url") as mocked_func:
        mocked_func.return_value = mangafast_search_html
        mangasearch = MangaFast()
        results = mangasearch.search("a query")
        assert expected == results
