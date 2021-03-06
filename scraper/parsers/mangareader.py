"""
HTML parsers that scrape and parse data from MangaReader.net
"""

import json
import logging
import re
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from scraper.exceptions import MangaDoesNotExist, VolumeDoesntExist
from scraper.new_types import SearchResults
from scraper.parsers.base import BaseMangaParser, BaseSearchParser, BaseSiteParser
from scraper.utils import get_html_from_url

logger = logging.getLogger(__name__)


class MangaReaderMangaParser(BaseMangaParser):
    """
    Scrapes & parses a specific manga page on mangareader.net
    """

    def __init__(
        self, manga_name: str, base_url: str = "http://mangareader.net"
    ) -> None:
        super().__init__(manga_name, base_url)

    def _scrape_volume(self, volume: int) -> BeautifulSoup:
        """
        Retrieve HTML for a given manga volume number
        """
        try:
            volume_html = get_html_from_url(f"{self.base_url}/{self.name}/{volume}")
            if not volume_html.text:
                raise MangaDoesNotExist(self.name)
            string = re.compile(".*not released yet.*")
            matches = volume_html.find_all(string=string, recursive=True)
            if matches:
                raise VolumeDoesntExist(f"Manga volume {volume} does not exist")
            return volume_html
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(f"Manga {self.name} does not exist")
            raise e

    def page_urls(self, volume: int) -> List[Tuple[int, str]]:
        """
        Return a list of urls for every page in a given volume
        """
        volume_html = self._scrape_volume(volume)
        scripts = volume_html.find_all("script")
        script = scripts[1]
        clean_script = script.text.replace('document["mj"]=', "")
        page_metadata = json.loads(clean_script)
        image_urls = [(int(x["p"]), "https:" + x["u"]) for x in page_metadata["im"]]
        return image_urls

    def all_volume_numbers(self) -> Iterable[int]:
        """
        All volume numbers for a manga
        """
        try:
            url = f"{self.base_url}/{self.name}"
            manga_html = get_html_from_url(url)
            volume_tags = manga_html.find("div", id="chapterlist").find_all("a")
            volume_numbers = [
                int(vol.get("href").split("/")[-1]) for vol in volume_tags
            ]
            return volume_numbers
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(f"Manga {self.name} does not exist")
            raise e


class MangaReaderSearch(BaseSearchParser):
    """
    Parses search queries from mangareader.net/search
    """

    def __init__(self, query: str, base_url: str = "http://mangareader.net") -> None:
        super().__init__(query, base_url)
        self.manga_type: int = 0
        self.manga_status: int = 0
        self.order: int = 0
        self.genre: str = "0000000000000000000000000000000000000"

    def _extract_text(self, result: Tag) -> Dict[str, str]:
        """
        Extract the desired text from a HTML search result
        """
        manga_name = result.find("div", {"class": "d57"})
        title = manga_name.text
        manga_url = manga_name.find("a").get("href")
        chapters = result.find("div", {"class": "d58"}).text
        return {
            "title": title.replace("\n", ""),
            "manga_url": manga_url[1:],
            "chapters": re.sub(r"\D", "", chapters),
            "source": "mangareader",
        }

    def search(self, start: int = 1) -> SearchResults:
        """
        Extract each mangas metadata from the search results
        """
        url = (
            f"{self.base_url}/search/?w={self.query}&rd={self.manga_type}"
            f"&status={self.manga_status}&order=0&genre={self.genre}&p=0"
        )
        results = self._scrape_results(url, div_class="d54")
        metadata: Dict[str, Dict[str, str]] = {}
        for key, result in enumerate(results, start=start):
            manga_metadata = self._extract_text(result)
            metadata[str(key)] = manga_metadata
        return metadata


class MangaReader(BaseSiteParser):
    """
    Scraper & parser for mangareader.net
    """

    def __init__(self, manga_name: Optional[str] = None) -> None:
        super().__init__(
            manga_name=manga_name,
            base_url="http://mangareader.net",
            manga_parser=MangaReaderMangaParser,
            search_parser=MangaReaderSearch,
        )
