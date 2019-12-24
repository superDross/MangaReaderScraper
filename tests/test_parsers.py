from unittest import mock

import pytest
import requests

from scraper.exceptions import MangaDoesNotExist, MangaParserNotSet
from scraper.parsers.mangakaka import MangaKaka, MangaKakaMangaParser
from scraper.parsers.mangareader import MangaReader, MangaReaderMangaParser


@pytest.mark.parametrize("siteparser", [MangaKaka, MangaReader])
def test_manga_not_set_error(siteparser):
    mr = siteparser()
    with pytest.raises(MangaParserNotSet):
        mr.manga


@pytest.mark.parametrize(
    "siteparser,mangaparser",
    [(MangaKaka, MangaKakaMangaParser), (MangaReader, MangaReaderMangaParser)],
)
def test_initialises_manga_parser(siteparser, mangaparser):
    mr = siteparser("dragon-ball")
    manga_parser = mr.manga
    assert isinstance(manga_parser, mangaparser)
    assert manga_parser.name == "dragon-ball"


@pytest.mark.parametrize(
    "siteparser,mangaparser",
    [(MangaKaka, MangaKakaMangaParser), (MangaReader, MangaReaderMangaParser)],
)
def test_set_manga_parser(siteparser, mangaparser):
    mr = siteparser()
    mr.manga = "dragon-ball"
    manga_parser = mr.manga
    assert isinstance(manga_parser, mangaparser)
    assert manga_parser.name == "dragon-ball"


@pytest.mark.parametrize("mangaparser", [MangaKakaMangaParser, MangaReaderMangaParser])
@mock.patch("scraper.utils.requests.get")
def test_404_errors(mock_request, mangaparser):
    mock_resp = requests.models.Response()
    mock_resp.status_code = 404
    mock_request.return_value = mock_resp
    parser = mangaparser("blahblahblah")
    with pytest.raises(MangaDoesNotExist):
        parser.all_volume_numbers()
    with pytest.raises(MangaDoesNotExist):
        parser.page_urls(1)


@pytest.mark.parametrize("mangaparser", [MangaKakaMangaParser, MangaReaderMangaParser])
@mock.patch("scraper.utils.requests.get")
def test_non_404_errors(mock_request, mangaparser):
    mock_resp = requests.models.Response()
    mock_resp.status_code = 403
    mock_request.return_value = mock_resp
    parser = mangaparser("blahblahblah")
    with pytest.raises(requests.exceptions.HTTPError):
        parser.all_volume_numbers()
