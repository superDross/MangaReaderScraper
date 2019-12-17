"""
HTML parsers that scrape and parse data from MangaReader.net
"""

import logging
import re
import sys
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from scraper.exceptions import MangaDoesNotExist, VolumeDoesntExist
from scraper.utils import get_html_from_url, settings

logger = logging.getLogger(__name__)

MANGA_URL = settings()["manga_url"]


class MangaReaderParser:
    """
    Parses data associated with a given manga name
    """

    def __init__(self, manga_name: str) -> None:
        self.manga_name = manga_name

    def _scrape_volume(self, volume) -> BeautifulSoup:
        """
        Retrieve HTML for a given manga volume number
        """
        try:
            volume_html = get_html_from_url(f"{MANGA_URL}/{self.manga_name}/{volume}")
            string = re.compile(".*not published.*")
            matches = volume_html.find_all(string=string, recursive=True)
            if matches:
                raise VolumeDoesntExist(self.manga_name, volume)
            return volume_html
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(self.manga_name)

    def page_urls(self, volume: int) -> List[str]:
        """
        Return a list of urls for every page in a given volume
        """
        volume_html = self._scrape_volume(volume)
        all_volume_links = volume_html.find_all("option")
        all_page_urls = [MANGA_URL + page.get("value") for page in all_volume_links]
        return all_page_urls

    def page_data(self, page_url: str) -> Tuple[int, bytes]:
        """
        Extracts a manga pages data
        """
        volume_num, page_num = page_url.split("/")[-2:]
        if not volume_num.isdigit():
            page_num = "1"
        page_html = get_html_from_url(page_url)
        img_url = page_html.find("img").get("src")
        img_data = requests.get(img_url).content
        return (int(page_num), img_data)

    def all_volume_numbers(self) -> List[int]:
        """
        All volume numbers for a manga
        """
        try:
            url = f"{MANGA_URL}/{self.manga_name}"
            manga_html = get_html_from_url(url)
            volume_tags = manga_html.find("div", id="chapterlist").find_all("a")
            volume_numbers = [
                int(vol.get("href").split("/")[-1]) for vol in volume_tags
            ]
            return volume_numbers
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MangaDoesNotExist(self.manga_name)
            raise e


class MangaReaderSearch:
    """
    Parse search queries to the site
    """

    def __init__(self, query: List[str]):
        self.query: List[str] = query
        self.manga_type: int = 0
        self.manga_status: int = 0
        self.order: int = 0
        self.genre: str = "0000000000000000000000000000000000000"

        self.results: List[Tag]

    def _scrape_results(self) -> List[Tag]:
        """
        Scrape and return HTML list with search results
        """
        query = "_".join(self.query)
        url = (
            f"{MANGA_URL}/search/?w={self.query}&rd={self.manga_type}"
            f"&status={self.manga_status}&order=0&genre={self.genre}&p=0"
        )
        html_response = get_html_from_url(url)
        search_results = html_response.find_all("div", {"class": "mangaresultitem"})
        if not search_results:
            logging.warning(f"No search results found for {query}")
            # TODO: raise error instead, then catch in __main__ and sys.exit?
            sys.exit()

        self.results = search_results
        return search_results

    def _extract_text(self, result: Tag) -> Dict[str, str]:
        """
        Extract the desired text from a HTML search result
        """
        manga_name = result.find("div", {"class": "manga_name"})
        title = manga_name.text
        manga_url = manga_name.find("a").get("href")
        chapters = result.find("div", {"class": "chapter_count"}).text
        manga_type = result.find("div", {"class": "manga_type"}).text
        return {
            "title": title.replace("\n", ""),
            "manga_url": manga_url[1:],
            "chapters": re.sub(r"\D", "", chapters),
            "type": manga_type.split("(")[0],
        }

    def metadata(self) -> Dict[str, Dict[str, str]]:
        """
        Extract each mangas metadata from the search results
        """
        results = self._scrape_results()
        metadata: Dict[str, Dict[str, str]] = {}
        for key, result in enumerate(results, start=1):
            manga_metadata = self._extract_text(result)
            metadata[str(key)] = manga_metadata
        return metadata
