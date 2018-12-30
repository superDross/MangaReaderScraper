import functools
import logging
import time

import requests
import bs4

logger = logging.getLogger(__name__)


def get_html_from_url(url):
    ''' Download the HTML text from a given url.'''
    req = requests.get(url)
    req.raise_for_status()
    url = bs4.BeautifulSoup(req.text, features='lxml')
    return url


def download_timer(func):
    ''' Manga volume(s) download timer.'''
    @functools.wraps(func)
    def wrapper_timer(*args):
        ''' Assumes last arg is the volume digit.'''
        start = time.time()
        returned = func(*args)
        run_time = round(time.time() - start, 1)
        if len(args) > 1:
            logging.info(f'Volume {args[-1]} downloaded in {run_time} seconds')
        else:
            logging.info(f'All volumes downloaded in {run_time} seconds')
        return returned
    return wrapper_timer
