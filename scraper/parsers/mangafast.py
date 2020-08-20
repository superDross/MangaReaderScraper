import logging
import re
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from scraper.exceptions import MangaDoesNotExist, VolumeDoesntExist
from scraper.new_types import SearchResults
from scraper.parsers.base import BaseMangaParser, BaseSearchParser, BaseSiteParser
from scraper.utils import get_html_from_url

logger = logging.getLogger(__name__)


class MangaFastMangaParser(BaseMangaParser):
    def __init__(self, manga_name: str, base_url: str = "http://mangafast.net") -> None:
        super().__init__(manga_name, base_url)

    def _scrape_volume(self, volume: int) -> BeautifulSoup:
        highest_volume = self.all_volume_numbers()[0]
        if volume > highest_volume:
            raise VolumeDoesntExist(f"Manga volume {volume} does not exist")
        try:
            volume_html = get_html_from_url(
                f"{self.base_url}/{self.name}-chapter-{volume}"
            )
            return volume_html
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(
                    f"Manga {self.name} or volume {volume} does not exist"
                )
            raise e

    def page_urls(self, volume: int) -> List[Tuple[int, str]]:
        volume_html = self._scrape_volume(volume)
        img_tags = volume_html.find("div", id="Read").find_all("img")
        img_urls: List[Tuple[int, str]] = []
        for page_num, url_tag in enumerate(img_tags, 1):
            url = url_tag.get("data-src")
            if page_num == 1:
                url = url_tag.get("src")
            img_urls.append((page_num, url))
        return img_urls

    def all_volume_numbers(self) -> List[int]:
        try:
            url = f"{self.base_url}/{self.name}?order=old#table"
            manga_html = get_html_from_url(url)
            volume_tags = manga_html.find("table", id="table").find_all("a")
            volume_tags = [tag for tag in volume_tags if tag.text != "PDF"]
            volume_numbers = [
                int(re.sub(r"\D", "", x.text.strip())) for x in volume_tags
            ]
            highest_volume = volume_numbers[0]
            return [vol for vol in volume_numbers if vol <= highest_volume]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(f"Manga {self.name} does not exist")
            raise e


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
            manga_parser=MangaFastMangaParser,
            search_parser=MangaFastSearch,
        )
