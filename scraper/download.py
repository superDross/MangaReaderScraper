"""
Downloads manga page images
"""

import logging
import os
from typing import List, Optional, Union

from scraper.manga import MangaFactory, Volume
from scraper.utils import download_timer, get_adapter

logger = logging.getLogger(__name__)


# TODO: create a single class that holds Download & Conversion as one via composition


class Download:
    def __init__(self, manga_name: str) -> None:
        self.factory = MangaFactory(manga_name)
        self.adapter = get_adapter(logger, manga_name)

    def _save_pages(self, volume: Volume) -> None:
        """
        Download volume page images from a given manga volume
        """
        for page in volume.pages:
            if not os.path.isfile(page.file_path):
                with open(page.file_path, "wb") as handler:
                    handler.write(page.img)

    @download_timer
    def download_volume(self, vol_num: Union[str, int]) -> None:
        """
        Download all pages of a given volume number
        """
        # TODO: adapter no longer working
        self.adapter.info(f"Downloading volume {vol_num}")
        volume = self.factory.get_manga_volume(vol_num)
        self._save_pages(volume)

    @download_timer
    def download_volumes(self, vol_nums: Optional[List[int]] = None) -> None:
        """
        Download all pages and volumes
        """
        volumes = self.factory.get_manga_volumes(vol_nums)
        for volume in volumes:
            self._save_pages(volume)
