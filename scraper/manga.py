"""
Manga building blocks & factories
"""

import os
from dataclasses import dataclass
from multiprocessing.pool import Pool, ThreadPool
from typing import Dict, List, Optional

from scraper.config import JPG_DIR, MANGA_DIR
from scraper.new_types import PageData, VolumeData
from scraper.parsers import MangaParser


@dataclass(frozen=True, repr=False)
class Page:
    """
    Holds page number, image data & file location
    """

    number: int
    img: bytes
    file_path: str

    def __repr__(self) -> str:
        img = True if self.img else False
        return f"Page(number={self.number}, img={img}, file_path={self.file_path})"

    def __str__(self) -> str:
        img = True if self.img else False
        return f"Page(number={self.number}, img={img}, file_path={self.file_path})"

    def save(self) -> None:
        """
        Save page image to disk
        """
        if not os.path.isfile(self.file_path):
            with open(self.file_path, "wb") as handler:
                handler.write(self.img)


class Volume:
    """
    Manga volume & its pages
    """

    def __init__(self, name: str, number: int, file_path: str) -> None:
        self.name: str = name
        self.number: int = number
        self.file_path: str = file_path
        self._pages: Dict[int, Page] = {}

    def __repr__(self) -> str:
        return f"Volume(number={self.number}, pages={len(self.pages)})"

    def __str__(self) -> str:
        return f"Volume(number={self.number}, pages={len(self.pages)})"

    def __iter__(self) -> Page:
        for page in self.pages:
            yield page

    def _page_path(self, page_number: int) -> str:
        return f"{JPG_DIR}/{self.name}_{self.number}_{page_number}.jpg"

    @property
    def page(self) -> None:
        return self._pages

    @property
    def pages(self) -> List[Page]:
        pages = self._pages.values()
        sorted_pages = sorted(pages, key=lambda x: x.number)
        return sorted_pages

    @pages.setter
    def pages(self, metadata: List[PageData]) -> None:
        self._pages = {}
        for page_number, img in metadata:
            page_file_path = self._page_path(page_number)
            page = Page(number=page_number, img=img, file_path=page_file_path,)
            self._pages[page_number] = page

    def add_page(self, page_number: int, img: bytes) -> None:
        """
        Appends a Page object from a page number & its image
        """
        if self.page.get(page_number):
            raise ValueError(f"Page {page_number} is already present")
        file_path = self._page_path(page_number)
        page = Page(number=page_number, img=img, file_path=file_path)
        self._pages[page_number] = page

    def total_pages(self) -> int:
        return max(self.pages[-1])


class Manga:
    def __init__(self, name: str, filetype: str = "pdf") -> None:
        self.name: str = name
        self.filetype: str = filetype
        self._volumes: Dict[int, Volume] = {}

    def __repr__(self) -> str:
        return f"Manga(name={self.name}, volumes={len(self.volumes)})"

    def __str__(self) -> str:
        return f"Manga(name={self.name}, volumes={len(self.volumes)})"

    def __iter__(self) -> Volume:
        for volume in self.volumes:
            yield volume

    def _volume_path(self, volume_number: int) -> str:
        return (
            f"{MANGA_DIR}/{self.name}/{self.name}"
            f"_volume_{volume_number}.{self.filetype}"
        )

    @property
    def volume(self) -> Dict[int, Volume]:
        return self._volumes

    @property
    def volumes(self) -> List[Volume]:
        volumes = self._volumes.values()
        sorted_volumes = sorted(volumes, key=lambda x: x.number)
        return sorted_volumes

    @volumes.setter
    def volumes(self, volumes: List[int]) -> None:
        self._volumes = {}
        for volume in volumes:
            self.add_volume(volume)

    def add_volume(self, volume_number: int) -> None:
        if self.volume.get(volume_number):
            raise ValueError(f"Volume {volume_number} is already present")
        vol_path = self._volume_path(volume_number)
        volume = Volume(name=self.name, number=volume_number, file_path=vol_path)
        self._volumes[volume.number] = volume

    def save(self) -> None:
        """
        Saves all manga volumes page images to disk
        """
        for volume in self.volumes:
            for page in volume.pages:
                page.save()


class MangaFactory:
    """
    Creates Manga objects
    """

    def __init__(self, manga_name: str) -> None:
        self.parser: MangaParser = MangaParser(manga_name)

    def __call__(self, volumes: Optional[List[int]] = None) -> Manga:
        return self.get_manga_volumes(volumes)

    def _get_volume_data(self, volume_number: int) -> VolumeData:
        """
        Returns volume number & each pages raw data
        """
        urls = self.parser.page_urls(volume_number)
        with ThreadPool() as pool:
            pages_data = pool.map(self.parser.page_data, urls)
        return (volume_number, pages_data)

    def _get_volumes_data(
        self, vol_nums: Optional[List[int]] = None
    ) -> List[VolumeData]:
        """
        Returns list of raw volume data
        """
        if not vol_nums:
            vol_nums = self.parser.all_volume_numbers()
        with Pool() as pool:
            return pool.map(self._get_volume_data, vol_nums)

    def get_manga_volumes(
        self, vol_nums: Optional[List[int]] = None, filetype: str = "pdf"
    ) -> Manga:
        """
        Returns a Manga object containing the requested volumes
        """
        volumes_data = self._get_volumes_data(vol_nums)
        manga = Manga(self.parser.manga_name, filetype)
        for volume_data in volumes_data:
            volume_number, pages_data = volume_data
            manga.add_volume(volume_number)
            manga.volume[volume_number].pages = pages_data
        return manga
