"""
Scrapes a given mangas volume(s) page images from MangaReader.net
"""

import logging
import os
from logging import Logger
from multiprocessing.pool import Pool, ThreadPool
from typing import Optional, Union

from scraper.config import JPG_DIR
from scraper.parsers import HTMLParser
from scraper.utils import CustomAdapter, download_timer, get_adapter

logger = logging.getLogger(__name__)


class DownloadManga:
    def __init__(self, manga: str) -> None:
        self.manga: str = manga
        self.volume: Optional[int] = None
        self.adapter: Union[Logger, CustomAdapter] = logger
        self.parser = HTMLParser(manga)

    def save_page(self, page: str) -> None:
        """
        Download volume page image from the given volume page url
        """
        page_filename = f"{JPG_DIR}/{self.manga}_{self.volume}_{page.number}.jpg"
        if not os.path.isfile(page_filename):
            with open(page_filename, "wb") as handler:
                handler.write(page.img)

    @download_timer
    def download_volume(self, volume: Union[str, int]) -> None:
        """
        Download all pages of a given volume number
        """
        self.volume = volume
        pages = self.parser.pages(volume)
        self.adapter = get_adapter(logger, self.manga, self.volume)
        self.adapter.info("Downloading")
        for page in pages:
            self.save_page(page)

    @download_timer
    def download_volumes(self, volumes: str) -> None:
        start, end = volumes.replace(" ", "").split("-")
        if not start.isdigit() and not end.isdigit():
            raise TypeError("volumes must contain digits")
        all_vols = [vol for vol in range(int(start), int(end) + 1)]
        with Pool() as pool:
            pool.map(self.download_volume, all_vols)

    @download_timer
    def download_all_volumes(self) -> None:
        """
        Download all pages and volumes
        """
        all_volume_numbers = self.parser.volumes()
        with Pool() as pool:
            pool.map(self.download_volume, all_volume_numbers)


def download_manga(manga: str, volume: Union[str, int]) -> None:
    downloader = DownloadManga(manga)
    if not os.path.exists(JPG_DIR):
        os.makedirs(JPG_DIR)
    if not volume:
        downloader.download_all_volumes()
    elif isinstance(volume, int) or volume.isdigit():
        downloader.download_volume(volume)
    elif isinstance(volume, str):
        downloader.download_volumes(volume)
    else:
        raise ValueError(f"Unknown volume: {volume}")
