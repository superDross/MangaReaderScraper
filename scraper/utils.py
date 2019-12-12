import configparser
import functools
import logging
import os
import time
from logging import Logger, LoggerAdapter
from typing import Any, Callable, Optional, Tuple

import bs4
import requests

logger = logging.getLogger(__name__)


class CustomAdapter(LoggerAdapter):
    """
    Prepends manga name & volume to the logger message
    """

    def process(self, msg: str, kwargs: dict) -> Tuple[str, dict]:
        manga = self.extra.get("manga").replace("-", " ").title()
        volume = self.extra.get("volume")
        if volume:
            return f"[{manga}:{volume}] {msg}", kwargs
        return f"[{manga}] {msg}", kwargs


def get_adapter(
    logger: Logger, manga: str, volume: Optional[str] = None
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

    user_home = os.path.expanduser("~")
    config["config"]["manga_directory"] = f"{user_home}/Downloads"
    config["config"]["manga_url"] = "http://mangareader.net"

    configpath = f"{user_home}/.config/mangascraper.ini"
    with open(configpath, "w") as configfile:
        config.write(configfile)


def settings() -> configparser.SectionProxy:
    """
    Retrieve settings file contents
    """
    config = configparser.ConfigParser()
    user_config = f"{os.path.expanduser('~')}/.config/mangascraper.ini"
    if not os.path.exists(user_config):
        create_base_config()
    config.read(user_config)
    return config["config"]
