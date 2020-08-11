import logging
import re
from typing import Dict, Iterable, List, Optional, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag

from scraper.new_types import SearchResults
from scraper.parsers.base import BaseMangaParser, BaseSearchParser, BaseSiteParser

logger = logging.getLogger(__name__)


class MangaFastParser(BaseMangaParser):
    def __init__(self, manga_name: str, base_url: str = "http://mangafast.net") -> None:
        super().__init__(manga_name, base_url)

    def _scrape_volume(self, volume: int) -> BeautifulSoup:
        pass

    def page_urls(self, volume: int) -> List[Tuple[int, str]]:
        pass

    def page_data(self, page_url: Tuple[int, str]) -> Tuple[int, bytes]:
        pass

    def all_volume_numbers(self) -> Iterable[int]:
        pass


class MangaFastSearch(BaseSearchParser):
    def __init__(self, query: str, base_url: str = "https://mangafast.net") -> None:
        super().__init__(query, base_url)

    def _extract_text(self, result: Tag) -> Dict[str, str]:
        title = result.find("h3").text.strip()
        manga_url = result.find("a").get("href")
        chapters = result.find("b").text
        return {
            "title": title,
            "manga_url": manga_url.split("/")[-2],
            "chapters": re.sub(r"\D", "", chapters),
            "source": "mangafast",
        }

    def search(self, start: int = 1) -> SearchResults:
        """
        Extract each mangas metadata from the search results
        """
        url = f"{self.base_url}/?s={self.query}"
        results = self._scrape_results(url, div_class="ls5")
        metadata: Dict[str, Dict[str, str]] = {}
        for key, result in enumerate(results, start=start):
            manga_metadata = self._extract_text(result)
            metadata[str(key)] = manga_metadata
        return metadata


class MangaFast(BaseSiteParser):
    """
    Scraper & parser for mangareader.net
    """

    def __init__(self, manga_name: Optional[str] = None) -> None:
        super().__init__(
            manga_name=manga_name,
            base_url="http://mangafast.net",
            manga_parser=MangaFastParser,
            search_parser=MangaFastSearch,
        )
