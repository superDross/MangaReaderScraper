from typing import Union

from scraper.parsers.mangareader import (
    MangaReader,
    MangaReaderMangaParser,
    MangaReaderSearch,
)
from scraper.parsers.mangakaka import (
    MangaKaka,
    MangaKakaMangaParser,
    MangaKakaSearch,
)
from scraper.parsers.mangaowl import (
    MangaOwl,
    MangaOwlParser,
    MangaOwlSearch,
)

MangaParser = Union[MangaReaderMangaParser, MangaKakaMangaParser, MangaOwlParser]
SearchParser = Union[MangaReaderSearch, MangaKakaSearch, MangaOwlSearch]
SiteParser = Union[MangaReader, MangaKaka, MangaOwl]
