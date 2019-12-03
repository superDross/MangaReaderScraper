""" Converts manga volume(s) images to a pdf or cbz file."""
import logging
import os
import re
import zipfile
from logging import Logger
from typing import List, Union

from PIL import Image

from reportlab.pdfgen import canvas
from scraper.config import JPG_DIR, MANGA_DIR
from scraper.utils import CustomAdapter, get_adapter

logger = logging.getLogger(__name__)


class Conversion:
    def __init__(self, manga: str) -> None:
        self.manga: str = manga
        self.volume: int = None
        self.images: List[str] = []
        self._type: str = "pdf"
        self.filename: str = None
        self.adapter: Union[Logger, CustomAdapter] = logging

    @property
    def type(self) -> str:
        """ Describes file type to convert to."""
        return self._type

    @type.setter
    def type(self, file_type: str) -> None:
        accepted = ["pdf", "cbz"]
        if file_type not in accepted:
            raise ValueError(f"{file_type} not accepted. Must be in {accepted}")
        self._type = file_type

    def _get_volume_images(self) -> None:
        """ Sort and return a list of all images of a specfic manga volume."""
        for jpg in os.listdir(JPG_DIR):
            if jpg.endswith("jpg") and self.manga in jpg:
                volume = jpg.split("_")[1]
                if int(volume) == int(self.volume):
                    self.images.append(jpg)

    def _get_page_number(self, page: str) -> int:
        """ Extract the page number from a given page url."""
        return int(re.split(r"[_.]", page)[-2])

    def _sort_images(self) -> None:
        """ Sort all images by page number."""
        sorted_volume = sorted(self.images, key=self._get_page_number)
        fully_sorted_volume = [os.path.join(JPG_DIR, x) for x in sorted_volume]
        self.images = fully_sorted_volume

    def _set_filename(self) -> None:
        """ Set filename for converted pdf/cbz file."""
        basename = f"{self.manga}_volume_{self.volume}.{self.type}"
        self.filename = os.path.join(MANGA_DIR, self.manga, basename)

    def _create_manga_dir(self) -> None:
        """ Create a manga directory if it does not exist."""
        manga_dir = os.path.join(MANGA_DIR, self.manga)
        if not os.path.exists(manga_dir):
            os.makedirs(manga_dir)

    def _convert_to_pdf(self) -> None:
        """ Convert all images to a PDF file."""
        c = canvas.Canvas(self.filename)
        for page in self.images:
            cover = Image.open(page)
            width, height = cover.size
            c.setPageSize((width, height))
            c.drawImage(page, x=0, y=0)
            c.showPage()
        c.save()

    def _convert_to_cbz(self) -> None:
        """ Convert all images to a CBZ file."""
        with zipfile.ZipFile(self.filename, "w") as cbz:
            for page in self.images:
                cbz.write(page, page)

    def _get_conversion_method(self) -> None:
        """ Returns the appropriate image conversion method."""
        conversion_method = {"pdf": self._convert_to_pdf, "cbz": self._convert_to_cbz}
        return conversion_method.get(self.type)

    def convert_volume(self, volume: int) -> None:
        """ Convert images of a specific volume number to a pdf/cbz file."""
        self.volume = volume
        self.adapter = get_adapter(logger, self.manga, self.volume)
        self._get_volume_images()
        self._sort_images()
        self._set_filename()
        self._create_manga_dir()
        converter = self._get_conversion_method()
        converter()
        self.adapter.info(f"Created {self.filename}")

    def convert_volumes(self, volumes: str) -> None:
        start, end = volumes.replace(" ", "").split("-")
        if not start.isdigit() and not end.isdigit():
            raise TypeError("volumes arg must be a number")
        all_vols = [vol for vol in range(int(start), int(end) + 1)]
        for volume in sorted(all_vols):
            self.convert_volume(volume)
            self.images = []

    def convert_all_volumes(self) -> None:
        """ Convert all images to their respective volume pdf/cbz files."""
        volumes = set(x.split("_")[1] for x in os.listdir(JPG_DIR) if self.manga in x)
        for volume in sorted(volumes):
            self.convert_volume(volume)
            self.images = []


def convert(manga: str, volume: int, cbz: bool) -> None:
    conversion = Conversion(manga)
    conversion.type = "cbz" if cbz else "pdf"
    if not os.path.exists(MANGA_DIR):
        os.makedirs(MANGA_DIR)
    if not volume:
        conversion.convert_all_volumes()
    elif volume.isdigit() or isinstance(volume, int):
        conversion.convert_volume(volume)
    elif isinstance(volume, str):
        conversion.convert_volumes(volume)
    else:
        raise ValueError(f"Unknown volume: {volume}")
