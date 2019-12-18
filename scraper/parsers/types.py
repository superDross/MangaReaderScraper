from typing import Type, Union

from scraper.parsers.mangareader import (
    MangaReader,
    MangaReaderMangaParser,
    MangaReaderSearch,
)

MangaParser = Union[MangaReaderMangaParser]
SearchParser = Union[MangaReaderSearch]
SiteParser = Union[MangaReader]

# unintialised classes
MangaParserClass = Union[Type[MangaReaderMangaParser]]
SearchParserClass = Union[Type[MangaReaderSearch]]
SiteParserClass = Union[Type[MangaReader]]
