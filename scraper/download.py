"""
Downloads manga page images
"""

import logging
import os
from typing import List, Optional, Union

from scraper.config import MANGA_DIR
from scraper.manga import Manga, MangaFactory, Volume
from scraper.utils import download_timer, get_adapter

logger = logging.getLogger(__name__)


# TODO: create a single class that holds Download & Conversion as one via composition


class Download:
    def __init__(self, manga_name: str) -> None:
        self.factory = MangaFactory(manga_name)
        self.adapter = get_adapter(logger, manga_name)

    @download_timer
    def download_volumes(self, vol_nums: Optional[List[int]] = None) -> None:
        """
        Download all pages and volumes
        """
        # self.adapter.info(f"Downloading volume {vol_num}")
        manga = self.factory.get_manga_volumes(vol_nums)
        manga.save()
