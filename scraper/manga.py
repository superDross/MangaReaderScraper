"""
Manga building blocks & factories
"""

from dataclasses import dataclass
from multiprocessing.pool import Pool, ThreadPool
from typing import List, Optional, Tuple

from scraper.config import JPG_DIR
from scraper.parsers import MangaParser


@dataclass
class Page:
    """
    Holds page number, is corresponding image & location
    """

    number: int
    img: bytes
    file_path: str


class Volume:
    """
    Manga volume & its pages
    """

    def __init__(self, name: str, number: str) -> None:
        self.name: str = name
        self.number: str = number
        self._pages: List[Page] = []

    def __repr__(self) -> None:
        return f"{self.name}: {self.number}"

    def __str__(self) -> None:
        return f"{self.name}: {self.number}"

    def _sort_pages(self) -> None:
        """
        Sort by page number
        """
        self._pages = sorted(self._pages, key=lambda x: x.number)

    def _page_path(self, page_number):
        return f"{JPG_DIR}/{self.name}_{self.number}_{page_number}.jpg"

    @property
    def pages(self) -> None:
        return self._pages

    @pages.setter
    def pages(self, metadata: List[Tuple[int, bytes]]) -> None:

        self._pages = [
            Page(number, img, self._page_path(number)) for number, img in metadata
        ]
        self._sort_pages()

    def add_page(self, page_number: int, img: bytes) -> None:
        """
        Appends a Page object from a page number & its image
        """
        file_path = self._page_path(page_number)
        page = Page(number=page_number, img=img, file_path=file_path)
        self._pages.append(page)
        self._sort_pages()


class MangaFactory:
    """
    Creates Volume objects
    """

    def __init__(self, manga_name):
        self.parser = MangaParser(manga_name)

    def get_manga_volume(self, vol_num: int) -> Volume:
        """
        Returns a manga volume object
        """
        volume = Volume(name=self.parser.manga_name, number=vol_num)
        urls = self.parser.page_urls(vol_num)
        with ThreadPool() as pool:
            pages_metadata = pool.map(self.parser.page_data, urls)
        volume.pages = pages_metadata
        return volume

    def get_manga_volumes(self, vol_nums: Optional[List[int]] = None) -> List[Volume]:
        """
        Returns all volumes objects from a given manga
        """
        if not vol_nums:
            vol_nums = self.parser.all_volume_numbers()
        with Pool() as pool:
            return pool.map(self.get_manga_volume, vol_nums)
