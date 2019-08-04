""" Scrapes a given mangas volume(s) page images from MangaReader.net."""
import logging
import os
import re
from multiprocessing.pool import Pool, ThreadPool

import requests

import custom_exceptions
from config import JPG_DIR, MANGA_URL
from utils import download_timer, get_html_from_url

logger = logging.getLogger(__name__)


class DownloadManga:
    def __init__(self, manga):
        self.manga = manga
        self.volume = None

    def _get_all_volume_urls(self):
        """ Return a list of urls for all manga volumes."""
        link = f"{MANGA_URL}/{self.manga}"
        manga_html = get_html_from_url(link)
        volume_tags = manga_html.find("div", id="chapterlist").find_all("a")
        volume_links = [MANGA_URL + vol.get("href") for vol in volume_tags]
        return volume_links

    def _get_volume_html_text(self):
        """ Retrieve HTML for a given manga volume number."""
        volume_html = get_html_from_url(f"{MANGA_URL}/{self.manga}/{self.volume}")
        return volume_html

    def _get_all_volume_pages_urls(self, volume_html):
        """ Return a list of urls for every page in a given volume."""
        all_volume_links = volume_html.find_all("option")
        all_page_urls = [MANGA_URL + page.get("value") for page in all_volume_links]
        return all_page_urls

    def _check_volume_exists(self, volume_html):
        """ Raise an exception if a given manga volume doesn't exist."""
        string = re.compile(".*not published.*")
        matches = volume_html.find_all(string=string, recursive=True)
        if matches:
            raise custom_exceptions.VolumeDoesntExist(self.manga, self.volume)

    def _get_page_filename(self, page_url):
        """ Constructs a volume page filename from a given volume page url."""
        volume_num, page_num = page_url.split("/")[-2:]
        if not volume_num.isdigit():
            page_num = 1
        jpg_filename = f"{self.manga}_{self.volume}_{page_num}.jpg"
        page_filename = os.path.join(JPG_DIR, jpg_filename)
        return page_filename

    def download_page(self, page_url):
        """ Download volume page image from the given volume page url."""
        page_html = get_html_from_url(page_url)
        page_filename = self._get_page_filename(page_url)
        if not os.path.isfile(page_filename):
            img_url = page_html.find("img").get("src")
            img_data = requests.get(img_url).content
            with open(page_filename, "wb") as handler:
                handler.write(img_data)

    @download_timer
    def download_volume(self, volume):
        """ Download all pages of a given volume number."""
        self.volume = volume
        volume_html = self._get_volume_html_text()
        self._check_volume_exists(volume_html)
        volume_page_urls = self._get_all_volume_pages_urls(volume_html)
        logging.info(
            f'Downloading {self.manga.replace("-", " ").title()} '
            f"Volume {self.volume}"
        )
        # Threading as it is a matter of IO.
        with ThreadPool() as pool:
            pool.map(self.download_page, volume_page_urls)

    @download_timer
    def download_volumes(self, volumes):
        start, end = volumes.replace(" ", "").split("-")
        if not start.isdigit() and not end.isdigit():
            raise TypeError("Must be thing")
        all_vols = [vol for vol in range(int(start), int(end) + 1)]
        with Pool() as pool:
            pool.map(self.download_volume, all_vols)

    @download_timer
    def download_all_volumes(self):
        """ Download all pages and volumes."""
        all_volumes = self._get_all_volume_urls()
        all_volume_numbers = [vol.split("/")[-1] for vol in all_volumes]
        with Pool() as pool:
            pool.map(self.download_volume, all_volume_numbers)


def download_manga(manga, volume):
    downloader = DownloadManga(manga)
    if not os.path.exists(JPG_DIR):
        os.makedirs(JPG_DIR)
    if not volume:
        downloader.download_all_volumes()
    elif volume.isdigit() or isinstance(volume, int):
        downloader.download_volume(volume)
    elif isinstance(volume, str):
        downloader.download_volumes(volume)
    else:
        raise ValueError(f"Unknown volume: {volume}")
