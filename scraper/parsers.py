"""
HTML parsers that scrape and parse data from MangaReader.net
"""

import re
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

from scraper.exceptions import VolumeDoesntExist
from scraper.utils import get_html_from_url, settings

MANGA_URL = settings()["manga_url"]


class MangaParser:
    """
    Parses data associated with a given manga name
    """

    def __init__(self, manga_name: str) -> None:
        self.manga_name = manga_name

    def _scrape_volume(self, volume) -> BeautifulSoup:
        """
        Retrieve HTML for a given manga volume number
        """
        volume_html = get_html_from_url(f"{MANGA_URL}/{self.manga_name}/{volume}")
        string = re.compile(".*not published.*")
        matches = volume_html.find_all(string=string, recursive=True)
        if matches:
            raise VolumeDoesntExist(self.manga_name, volume)
        return volume_html

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
        Returns a Page object by scraping from a given url
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
        url = f"{MANGA_URL}/{self.manga_name}"
        manga_html = get_html_from_url(url)
        volume_tags = manga_html.find("div", id="chapterlist").find_all("a")
        volume_numbers = [int(vol.get("href").split("/")[-1]) for vol in volume_tags]
        return volume_numbers


def get_search_results(
    query: str,
    manga_type: int = 0,
    manga_status: int = 0,
    order: int = 0,
    genre: str = "0000000000000000000000000000000000000",
) -> List[str]:
    """
    Scrape and return HTML dict with search results
    """
    # TODO: change to class when integrating args e.g. genre
    url = f"""{MANGA_URL}/search/?w={query}&rd={manga_type}
               &status={manga_status}&order=0&genre={genre}&p=0"""
    html_response = get_html_from_url(url)
    search_results = html_response.find_all("div", {"class": "mangaresultitem"})
    return search_results
