from unittest import mock
from scraper.download import Download


def test_download_manga_as_pdf(parser):
    with mock.patch("scraper.manga.MangaParser", parser):
        downloader = Download("dragon-ball", "pdf")
        downloader.download_volumes([1])
