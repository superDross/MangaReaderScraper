import functools
import logging
import time
from logging import Logger, LoggerAdapter
from typing import Callable, Tuple

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


def get_adapter(logger: Logger, manga: str, volume: str) -> CustomAdapter:
    extra = {"manga": manga, "volume": volume}
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
    def wrapper_timer(*args):
        """
        Assumes last arg is the volume digit
        """
        start = time.time()
        returned = func(*args)
        run_time = round(time.time() - start, 1)
        if len(args) > 1:
            logging.info(f"Volume {args[-1]} downloaded in {run_time} seconds")
        else:
            logging.info(f"All volumes downloaded in {run_time} seconds")
        return returned

    return wrapper_timer
