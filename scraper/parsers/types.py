from typing import Type, Union

from scraper.parsers.mangakaka import MangaKaka, MangaKakaMangaParser, MangaKakaSearch
from scraper.parsers.mangafast import MangaFast, MangaFastMangaParser, MangaFastSearch
from scraper.parsers.mangareader import (
    MangaReader,
    MangaReaderMangaParser,
    MangaReaderSearch,
)

MangaParser = Union[MangaReaderMangaParser, MangaKakaMangaParser, MangaFastMangaParser]
SearchParser = Union[MangaReaderSearch, MangaKakaSearch, MangaFastSearch]
SiteParser = Union[MangaReader, MangaKaka, MangaFast]


MangaParserClass = Union[
    Type[MangaReaderMangaParser], Type[MangaKakaMangaParser], Type[MangaFastMangaParser]
]
SearchParserClass = Union[
    Type[MangaReaderSearch], Type[MangaKakaSearch], Type[MangaFastSearch]
]
SiteParserClass = Union[Type[MangaReader], Type[MangaKaka], Type[MangaFast]]
