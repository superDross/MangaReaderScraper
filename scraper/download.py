"""
Downloads manga page images
"""

import logging
import os
import zipfile
from multiprocessing.pool import Pool
from typing import Callable, List, Optional

from PIL import Image
from reportlab.pdfgen import canvas

from scraper.config import MANGA_DIR
from scraper.manga import MangaFactory, Volume
from scraper.utils import download_timer, get_adapter

logger = logging.getLogger(__name__)


class Download:
    """
    Downloads the manga in the desired format
    """

    def __init__(self, manga_name: str, filetype: str) -> None:
        self.factory = MangaFactory(manga_name)
        self.adapter = get_adapter(logger, manga_name)
        self.type = filetype

    def _create_manga_dir(self, manga_name: str) -> None:
        """
        Create a manga directory if it does not exist.
        """
        manga_dir = os.path.join(MANGA_DIR, manga_name)
        if not os.path.exists(manga_dir):
            os.makedirs(manga_dir)

    def _to_pdf(self, volume: Volume) -> None:
        """
        Convert all page images to a PDF file.
        """
        # TODO: possible to add page.img instead of filepath?
        #       this would mean we would not have to save images to disk
        c = canvas.Canvas(volume.file_path)
        for page in volume.pages:
            cover = Image.open(page.file_path)
            width, height = cover.size
            c.setPageSize((width, height))
            c.drawImage(page.file_path, x=0, y=0)
            c.showPage()
        c.save()

    def _to_cbz(self, volume: Volume) -> None:
        """
        Convert all page images to a CBZ file.
        """
        with zipfile.ZipFile(volume.file_path, "w") as cbz:
            for page in volume.pages:
                cbz.write(page.file_path, page.file_path)

    def _get_save_method(self) -> Callable:
        """
        Returns the appropriate image conversion method.
        """
        conversion_method = {"pdf": self._to_pdf, "cbz": self._to_cbz}
        return conversion_method.get(self.type)

    @download_timer
    def download_volumes(self, vol_nums: Optional[List[int]] = None) -> None:
        """
        Download all pages and volumes
        """
        self.adapter.info(f"Starting Downloads")
        manga = self.factory.get_manga_volumes(vol_nums, self.type)
        self._create_manga_dir(manga.name)
        manga.save()
        save_method = self._get_save_method()
        with Pool() as pool:
            pool.map(save_method, manga.volumes)
        self.adapter.info(f"All volumes downloaded")
