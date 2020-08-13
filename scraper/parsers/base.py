"""
Abstract base classes for all parsers
"""
import abc
import logging
import sys
from functools import lru_cache
from typing import Iterable, List, Optional, Tuple, Type

import requests
from bs4.element import Tag

from scraper.exceptions import MangaParserNotSet
from scraper.new_types import SearchResults
from scraper.utils import get_html_from_url

logger = logging.getLogger(__name__)


class BaseMangaParser:
    """
    Parses data associated with a given manga name
    """

    def __init__(self, manga_name: str, base_url: str) -> None:
        self.name = manga_name
        self.base_url = base_url

    @abc.abstractmethod
    def page_urls(self, volume: int) -> List[Tuple[int, str]]:
        """
        Return a list of urls for every page in a given volume
        """
        pass

    def page_data(self, page_url: Tuple[int, str]) -> Tuple[int, bytes]:
        """
        Extracts a manga pages data
        """
        page_num, img_url = page_url
        img_data = requests.get(img_url).content
        return (int(page_num), img_data)

    @abc.abstractmethod
    def all_volume_numbers(self) -> Iterable[int]:
        """
        All volume numbers for a manga
        """
        pass


class BaseSearchParser:
    """
    Parse search queries & returns the results
    """

    def __init__(self, query: str, base_url: str) -> None:
        self.query: str = query
        self.base_url: str = base_url

    def _scrape_results(self, url: str, div_class: str) -> List[Tag]:
        """
        Scrape and return HTML list with search results
        """
        html_response = get_html_from_url(url)
        search_results = html_response.find_all("div", {"class": div_class})
        if not search_results:
            logging.warning(f"No search results found for {self.query}\nExiting...")
            sys.exit()
        self.results = search_results
        return search_results

    @abc.abstractmethod
    def search(self, start: int = 1) -> SearchResults:
        """
        Extract each mangas metadata from the search results
        """
        pass


class BaseSiteParser:
    """
    Base parser for a specific manga website
    """

    __metaclass__ = abc.ABCMeta

    def __init__(
        self,
        base_url: str,
        manga_parser: Type[BaseMangaParser],
        search_parser: Type[BaseSearchParser],
        manga_name: Optional[str],
    ):
        self.base_url = base_url
        self._manga_parser = manga_parser
        self._search_parser = search_parser
        self._manga: Optional[BaseMangaParser] = (
            None if not manga_name else self._manga_parser(manga_name, base_url)
        )

    def __new__(cls, *args, **kwargs) -> "BaseSiteParser":
        if cls is BaseSiteParser:
            raise Exception("Abstract class cannot be instantiatied")
        return object.__new__(cls)

    @property
    def manga(self) -> BaseMangaParser:
        if self._manga:
            return self._manga
        raise MangaParserNotSet("No parser has been set")

    @manga.setter
    def manga(self, manga_name: str) -> None:
        self._manga = self._manga_parser(manga_name, self.base_url)

    @lru_cache()
    def search(self, query: str) -> SearchResults:
        search_parser = self._search_parser(query, self.base_url)
        return search_parser.search()
