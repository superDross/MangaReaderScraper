"""
HTML parser classes
"""
import re
from dataclasses import dataclass
from multiprocessing.pool import Pool, ThreadPool
from typing import List

import requests

from bs4 import BeautifulSoup
from scraper.config import MANGA_URL
from scraper.exceptions import MangaDoesNotExist, VolumeDoesntExist
from scraper.utils import get_html_from_url

# class Manga:
#     def __init__(self, name, volume):
#         self.name = name
#         self.volume = volume
#         self._pages: List[Page] = []

#     def __repr__(self):
#         return f"{self.name} - {self.volume}"

#     @property
#     def pages(self):
#         return self._pages

#     @pages.setter
#     def pages(self, *args) -> None:
#         raise NotImplementedError(
#             "The pages attribute cannot be set. Use the add_page method instead"
#         )

#     def add_page(self, page_number: int, img_url: str) -> None:
#         page = Page(manga=self, number=page_number, img_url=img_url)
#         self._pages.append(page)
#         self._pages = sorted(self._pages, key=lambda x: x.number)


@dataclass
class Page:
    number: int
    img: str


class HTMLParser:
    def __init__(self, manga: str) -> None:
        self.manga = manga

    def _scrape_volume(self, volume) -> BeautifulSoup:
        """
        Retrieve HTML for a given manga volume number
        """
        volume_html = get_html_from_url(f"{MANGA_URL}/{self.manga}/{volume}")
        string = re.compile(".*not published.*")
        matches = volume_html.find_all(string=string, recursive=True)
        if matches:
            raise VolumeDoesntExist(self.manga, volume)
        return volume_html

    def _page_urls(self, volume: int) -> List[str]:
        """
        Return a list of urls for every page in a given volume
        """
        volume_html = self._scrape_volume(volume)
        all_volume_links = volume_html.find_all("option")
        all_page_urls = [MANGA_URL + page.get("value") for page in all_volume_links]
        return all_page_urls

    def _page(self, page_url: str) -> Page:
        """
        Returns a Page object by scraping from a a given url
        """
        volume_num, page_num = page_url.split("/")[-2:]
        if not volume_num.isdigit():
            page_num = 1
        page_html = get_html_from_url(page_url)
        img_url = page_html.find("img").get("src")
        img_data = requests.get(img_url).content
        return Page(number=page_num, img=img_data)

    def volumes(self) -> List[str]:
        """
        All volume numbers for a manga
        """
        url = f"{MANGA_URL}/{self.manga}"
        manga_html = get_html_from_url(url)
        volume_tags = manga_html.find("div", id="chapterlist").find_all("a")
        volume_numbers = [vol.get("href").split("/")[-1] for vol in volume_tags]
        return volume_numbers

    def pages(self, volume: int) -> List[Page]:
        """
        Returns all Page objects associated with a volume
        """
        urls = self._page_urls(volume)
        with ThreadPool() as pool:
            return pool.map(self._page, urls)
