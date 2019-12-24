from typing import Type, Union

from scraper.parsers.mangakaka import MangaKaka, MangaKakaMangaParser, MangaKakaSearch
from scraper.parsers.mangareader import (
    MangaReader,
    MangaReaderMangaParser,
    MangaReaderSearch,
)

MangaParser = Union[MangaReaderMangaParser, MangaKakaMangaParser]
SearchParser = Union[MangaReaderSearch, MangaKakaSearch]
SiteParser = Union[MangaReader, MangaKaka]


MangaParserClass = Union[Type[MangaReaderMangaParser], Type[MangaKakaMangaParser]]
SearchParserClass = Union[Type[MangaReaderSearch], Type[MangaKakaSearch]]
SiteParserClass = Union[Type[MangaReader], Type[MangaKaka]]
