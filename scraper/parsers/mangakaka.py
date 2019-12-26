import logging
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from scraper.exceptions import MangaDoesNotExist, VolumeDoesntExist
from scraper.new_types import SearchResults
from scraper.parsers.base import BaseMangaParser, BaseSearchParser, BaseSiteParser
from scraper.utils import get_html_from_url

logger = logging.getLogger(__name__)


class MangaKakaMangaParser(BaseMangaParser):
    """
    Scrapes & parses a specific manga page on mangakakalot.com
    """

    def __init__(
        self, manga_name: str, base_url: str = "https://mangakakalot.com"
    ) -> None:
        super().__init__(manga_name, base_url)

    def _scrape_volume(self, volume: int) -> BeautifulSoup:
        """
        Retrieve HTML for a given manga volume number
        """
        try:
            url = f"https://manganelo.com/chapter/{self.name}/chapter_{volume}"
            volume_html = get_html_from_url(url)
            string = re.compile("404 NOT FOUND")
            matches = volume_html.find_all(string=string, recursive=True)
            if matches:
                raise VolumeDoesntExist(f"manga volume {volume} does not exist")
            return volume_html
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(f"manga {self.name} does not exist")

    def page_urls(self, volume: int) -> List[str]:
        """
        Return a list of urls for every page in a given volume
        """
        volume_html = self._scrape_volume(volume)
        container = volume_html.find("div", {"class": "container-chapter-reader"})
        all_img_tags = container.find_all("img")
        all_page_urls = [img.get("src") for img in all_img_tags]
        return all_page_urls

    def page_data(self, page_url: str, retries=1, max_retries=5) -> Tuple[int, bytes]:
        """
        Extracts a manga pages data
        """
        try:
            page_num = Path(page_url).stem
            img_data = requests.get(page_url).content
            return (int(page_num), img_data)
        except requests.exceptions.ConnectionError as e:
            if retries < max_retries:
                logger.info(f"Retrying to re-establish connection to {page_url}")
                return self.page_data(page_url, retries + 1, max_retries)
            raise e

    def _extract_number(self, vol_tag: Tag) -> int:
        """
        Sanitises a number from scraped chapter tag
        """
        vol_text = vol_tag.split("/")[-1].split("_")[-1]
        return int(round(float(vol_text)))

    def all_volume_numbers(self) -> Iterable[int]:
        """
        All volume numbers for a manga
        """
        try:
            url = f"https://manganelo.com/manga/{self.name}"
            manga_html = get_html_from_url(url)

            volume_tags = manga_html.find_all("li", {"class": "a-h"})
            volume_numbers = set(
                self._extract_number(vol.find("a").get("href")) for vol in volume_tags
            )
            return volume_numbers
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(f"manga {self.name} does not exist")
            raise e


class MangaKakaSearch(BaseSearchParser):
    """
    Parses search queries from mangakakaalot
    """

    def __init__(self, query: str, base_url: str = "https://mangakakalot.com") -> None:
        super().__init__(query, base_url)

    def _scrape_results(self) -> List[Tag]:
        """
        Scrape and return HTML list with search results
        """
        url = f"{self.base_url}/search/{self.query.replace(' ', '_')}"
        html_response = get_html_from_url(url)
        search_results = html_response.find_all("div", {"class": "story_item"})
        if not search_results:
            logging.warning(f"No search results found for {self.query}")
            # TODO: raise error instead, then catch in __main__ and sys.exit?
            sys.exit()

        self.results = search_results
        return search_results

    def _extract_text(self, result: Tag) -> Dict[str, str]:
        """
        Extract the desired text from a HTML search result
        """
        manga_name = result.find("img").get("alt")
        manga_url = result.find("a").get("href")
        last_chapter = result.find("em", {"class": "story_chapter"}).find("a")
        chapters = last_chapter.get("href").split("_")[-1]
        return {
            "title": manga_name,
            "manga_url": Path(manga_url).stem,
            "chapters": str(round(float(chapters))),
            "source": "mangakaka",
        }

    def search(self, start: int = 1) -> SearchResults:
        """
        Extract each mangas metadata from the search results
        """
        results = self._scrape_results()
        metadata = {}
        for key, result in enumerate(results, start=start):
            manga_metadata = self._extract_text(result)
            metadata[str(key)] = manga_metadata
        return metadata


class MangaKaka(BaseSiteParser):
    """
    Seems to be the same as manganelo.com

    Can probably use this class for manganelo too
    """

    def __init__(self, manga_name: Optional[str] = None) -> None:
        super().__init__(
            manga_name=manga_name,
            base_url="https://mangakakalot.com",
            manga_parser=MangaKakaMangaParser,
            search_parser=MangaKakaSearch,
        )
