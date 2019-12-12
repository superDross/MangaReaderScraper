"""
Manga building blocks & factories
"""

import logging
from dataclasses import dataclass, field
from multiprocessing.pool import Pool, ThreadPool
from typing import Dict, List, Optional

from scraper.exceptions import PageAlreadyPresent, VolumeAlreadyPresent
from scraper.new_types import PageData, VolumeData
from scraper.parsers import MangaParser
from scraper.utils import get_adapter, settings

logger = logging.getLogger(__name__)

MANGA_DIR = settings()["manga_directory"]


@dataclass(frozen=True, repr=False)
class Page:
    """
    Holds page number & its image
    """

    number: int
    img: bytes

    def __repr__(self) -> str:
        img = True if self.img else False
        return f"Page(number={self.number}, img={img})"

    def __str__(self) -> str:
        img = True if self.img else False
        return f"Page(number={self.number}, img={img})"


@dataclass
class Volume:
    """
    Manga volume & its pages
    """

    number: int
    file_path: str
    _pages: Dict[int, Page] = field(default_factory=dict, repr=False)

    def __repr__(self) -> str:
        return f"Volume(number={self.number}, pages={len(self.pages)})"

    def __str__(self) -> str:
        return f"Volume(number={self.number}, pages={len(self.pages)})"

    def __iter__(self) -> Page:
        for page in self.pages:
            yield page

    @property
    def page(self) -> Dict[int, Page]:
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
            page = Page(number=page_number, img=img)
            self._pages[page_number] = page

    def add_page(self, page_number: int, img: bytes) -> None:
        """
        Appends a Page object from a page number & its image
        """
        if self.page.get(page_number):
            raise PageAlreadyPresent(f"Page {page_number} is already present")
        page = Page(number=page_number, img=img)
        self._pages[page_number] = page

    def total_pages(self) -> int:
        return max(self.page)


@dataclass
class Manga:
    """
    Manga with volume and pages objects
    """

    name: str
    filetype: str
    _volumes: Dict[int, Volume] = field(default_factory=dict, repr=False)

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
            raise VolumeAlreadyPresent(f"Volume {volume_number} is already present")
        vol_path = self._volume_path(volume_number)
        volume = Volume(number=volume_number, file_path=vol_path)
        self._volumes[volume.number] = volume


class MangaBuilder:
    """
    Creates Manga objects
    """

    def __init__(self, manga_name: str) -> None:
        self.parser: MangaParser = MangaParser(manga_name)

    def _get_volume_data(self, volume_number: int) -> VolumeData:
        """
        Returns volume number & each pages raw data
        """
        adapter = get_adapter(logger, self.parser.manga_name, volume_number)
        adapter.info("downloading pages")
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
