"""
Manga building blocks & factories
"""

import logging
from dataclasses import dataclass, field
from multiprocessing.pool import Pool, ThreadPool
from pathlib import Path
from typing import Dict, Generator, List, Optional

from scraper.exceptions import (
    PageAlreadyPresent,
    VolumeAlreadyExists,
    VolumeAlreadyPresent,
    VolumeDoesntExist,
)
from scraper.new_types import PageData, VolumeData
from scraper.parsers.types import SiteParser
from scraper.utils import get_adapter, settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True, repr=False)
class Page:
    """
    Holds page number & its image
    """

    number: int
    img: bytes

    def __repr__(self) -> str:
        return self._str()

    def __str__(self) -> str:
        return self._str()

    def _str(self) -> str:
        img = True if self.img else False
        return f"Page(number={self.number}, img={img})"


@dataclass
class Volume:
    """
    Manga volume & its pages
    """

    number: int
    file_path: Path
    upload_path: Path
    _pages: Dict[int, Page] = field(default_factory=dict, repr=False)

    def __repr__(self) -> str:
        return self._str()

    def __str__(self) -> str:
        return self._str()

    def __eq__(self, other):
        attrs = [attr for attr in self.__dict__.keys()]
        return all(
            str(getattr(self, attr)) == str(getattr(other, attr)) for attr in attrs
        )

    def __iter__(self) -> Generator:
        for page in self.pages:
            yield page

    def _str(self) -> str:
        return f"Volume(number={self.number}, pages={len(self.pages)})"

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
            self.add_page(page_number, img)

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
        return self._str()

    def __str__(self) -> str:
        return self._str()

    def __iter__(self) -> Generator[Volume, None, None]:
        for volume in self.volumes:
            yield volume

    def _str(self) -> str:
        return f"Manga(name={self.name}, volumes={len(self.volumes)})"

    def _volume_path(self, volume_number: int) -> Path:
        manga_dir = settings()["config"]["manga_directory"]
        return Path(
            f"{manga_dir}/{self.name}/{self.name}"
            f"_volume_{volume_number}.{self.filetype}"
        )

    def _volume_upload_path(self, volume_number: int) -> Path:
        root = Path(settings()["config"]["upload_root"])
        return root / f"{self.name}/{self.name}_volume_{volume_number}.{self.filetype}"

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
        vol_upload_path = self._volume_upload_path(volume_number)
        # TODO: causes problems with uploading an already existant file
        #       it should logger.warning then return instead
        # TODO: MAYBE EASIER TO REMOVE THE EXCEPTION HANDELLING HERE
        if vol_path.exists():
            raise VolumeAlreadyExists(f"{str(vol_path)} already saved to disk")
        volume = Volume(
            number=volume_number, file_path=vol_path, upload_path=vol_upload_path
        )
        self._volumes[volume.number] = volume


class MangaBuilder:
    """
    Creates Manga objects
    """

    def __init__(self, parser: SiteParser) -> None:
        self.parser: SiteParser = parser

    def _get_volume_data(self, volume_number: int) -> VolumeData:
        """
        Returns volume number & each pages raw data
        """
        adapter = get_adapter(logger, self.parser.manga.name, volume_number)
        adapter.info("downloading pages")
        try:
            urls = self.parser.manga.page_urls(volume_number)
        except VolumeDoesntExist as e:
            adapter.warning(e)
        with ThreadPool() as pool:
            pages_data = pool.map(self.parser.manga.page_data, urls)
        return (volume_number, pages_data)

    def _get_volumes_data(
        self, vol_nums: Optional[List[int]] = None
    ) -> List[VolumeData]:
        """
        Returns list of raw volume data
        """
        volumes = self.parser.manga.all_volume_numbers() if not vol_nums else vol_nums
        with Pool() as pool:
            return pool.map(self._get_volume_data, volumes)

    def get_manga_volumes(
        self,
        vol_nums: Optional[List[int]] = None,
        filetype: str = "pdf",
        preferred_name: Optional[str] = None,
    ) -> Manga:
        """
        Returns a Manga object containing the requested volumes
        """
        volumes_data = self._get_volumes_data(vol_nums)
        manga_name = preferred_name if preferred_name else self.parser.manga.name
        manga = Manga(manga_name, filetype)
        for volume_data in volumes_data:
            try:
                volume_number, pages_data = volume_data
                manga.add_volume(volume_number)
                # properties cause an error in mypy when getter/setters input
                # differ, mypy thinks they should be the same
                manga.volume[volume_number].pages = pages_data  # type: ignore
            except (VolumeAlreadyExists, VolumeAlreadyPresent) as e:
                logger.warning(e)
        return manga
