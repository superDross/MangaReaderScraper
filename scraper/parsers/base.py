import abc
from functools import lru_cache
from typing import List, Tuple

from scraper.exceptions import MangaParserNotSet
from scraper.new_types import SearchResults


class BaseMangaParser:
    """
    Parses data associated with a given manga name
    """

    def __init__(self, manga_name: str, base_url: str) -> None:
        self.name = manga_name
        self.base_url = base_url

    def __call__(self, *args, **kwargs):
        """
        Required as mypy thinks you are trying to call an
        intiliased object and not actually initilise a class.
        Creating a naked __call__ method stops it from thinking
        the class is 'not callable'.
        """
        pass

    @abc.abstractmethod
    def page_urls(self, volume: int) -> List[str]:
        pass

    @abc.abstractmethod
    def page_data(self, page_url: str) -> Tuple[int, bytes]:
        pass

    @abc.abstractmethod
    def all_volume_numbers(self) -> List[int]:
        pass


class BaseSearchParser:
    """
    Parse search queries to manga reader
    """

    def __init__(self, query: List[str], base_url: str) -> None:
        self.query: List[str] = query
        self.base_url: str = base_url

    def __call__(self, *args, **kwargs):
        """
        Required as mypy thinks you are trying to call an
        intiliased object and not actually initilise a class.
        Creating a naked __call__ method stops it from thinking
        the class is 'not callable'.
        """
        pass

    @abc.abstractmethod
    def search(self, query) -> SearchResults:
        pass


class BaseSiteParser:
    """
    Base parser for a specific manga website
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, base_url, parser_class, search_class, manga_name):
        self.base_url = base_url
        self._parser_class = parser_class
        self._search_class = search_class
        self._manga = (
            None if not manga_name else self._parser_class(manga_name, base_url)
        )

    def __new__(cls, *args, **kwargs):
        if cls is BaseSiteParser:
            raise Exception("Abstract class cannot be instantiatied")
        return object.__new__(cls)

    def __call__(self, *args, **kwargs):
        """
        Required as mypy thinks you are trying to call an
        intiliased object and not actually initilise a class.
        Creating a naked __call__ method stops it from thinking
        the class is 'not callable'.
        """
        pass

    @property
    def manga(self):
        if self._manga:
            return self._manga
        raise MangaParserNotSet("No parser has been set")

    @manga.setter
    def manga(self, manga_name):
        self._manga = self._parser_class(manga_name, self.base_url)

    @lru_cache()
    def search(self, query):
        search_parser = self._search_class(query, self.base_url)
        return search_parser.search()
