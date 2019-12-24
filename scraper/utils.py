import configparser
import functools
import logging
import re
import time
from logging import Logger, LoggerAdapter
from pathlib import Path
from typing import Any, Callable, MutableMapping, Optional, Tuple, Union

import bs4
import requests

from scraper.exceptions import CannotExtractChapter

logger = logging.getLogger(__name__)


class CustomAdapter(LoggerAdapter):
    """
    Prepends manga name & volume to the logger message
    """

    def process(
        self, msg: str, kwargs: MutableMapping[str, Union[str, int]]
    ) -> Tuple[str, MutableMapping[str, Union[str, int]]]:
        manga = self.extra.get("manga")
        volume = self.extra.get("volume")
        if volume:
            return f"[{manga}:{volume}] {msg}", kwargs
        return f"[{manga}] {msg}", kwargs


def get_adapter(
    logger: Logger, manga: str, volume: Optional[Union[str, int]] = None
) -> CustomAdapter:
    if volume:
        extra = {"manga": manga, "volume": volume}
    else:
        extra = {"manga": manga}
    return CustomAdapter(logger, extra)


def get_html_from_url(url: str) -> bs4.BeautifulSoup:
    """
    Download the HTML text from a given url
    """
    req = requests.get(url)
    req.raise_for_status()
    html = bs4.BeautifulSoup(req.text, features="lxml")
    return html


def download_timer(func: Callable) -> Callable:
    """
    Manga volume(s) download timer
    """

    @functools.wraps(func)
    def wrapper_timer(*args) -> Any:
        """
        Assumes last arg is the volume digit
        """
        start = time.time()
        returned = func(*args)
        run_time = round(time.time() - start, 1)
        logging.info(f"Volumes downloaded in {run_time} seconds")
        return returned

    return wrapper_timer


def create_base_config() -> None:
    config = configparser.ConfigParser()
    config.add_section("config")

    user_home = Path.home()
    downloaddir = user_home / "Downloads"
    configdir = user_home / ".config"
    for path in [downloaddir, configdir]:
        path.mkdir(parents=True, exist_ok=True)

    config["config"]["manga_directory"] = str(downloaddir)
    config["config"]["source"] = "mangareader"

    configfile = configdir / "mangascraper.ini"
    with configfile.open("w") as cf:
        config.write(cf)


def settings() -> configparser.ConfigParser:
    """
    Retrieve settings file contents
    """
    config = configparser.ConfigParser()
    user_config = Path.home() / ".config" / "mangascraper.ini"
    if not user_config.exists():
        create_base_config()
    config.read(str(user_config))
    return config


def extract_chapter_number(chapter_string: str) -> str:
    """
    Extracts the chapter digit substring in a string that
    details manga chapter number
    """
    chapter_split = chapter_string.lower().split()
    if "chapter" not in chapter_split:
        raise CannotExtractChapter(
            f"Can't find chapter substring in {chapter_string.split()}"
        )
    chapter_name_index = chapter_split.index("chapter") + 1
    chapter_string = chapter_split[chapter_name_index]
    chapter_string_split = re.split(r"\D", chapter_string)
    if "" in chapter_string_split:
        chapter_string_split.remove("")
    chapter_number = chapter_string_split[0]
    if not chapter_number.isdigit():
        raise CannotExtractChapter(f"Cannot find chapter digit in {chapter_number}")
    if len(chapter_number) > 1 and chapter_number.startswith("0"):
        chapter_number = chapter_number.lstrip("0")
    return chapter_number
