import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Iterable

import requests
from bs4.element import Tag

from scraper.exceptions import (
    MangaDoesNotExist,
    VolumeDoesntExist,
    CannotExtractChapter,
)
from scraper.parsers.base import BaseMangaParser, BaseSearchParser, BaseSiteParser
from scraper.utils import get_html_from_url, extract_chapter_number
import logging

logger = logging.getLogger(__name__)


class MangaOwlParser(BaseMangaParser):
    def __init__(self, manga_name: str, base_url: str = "http://mangaowl.com") -> None:
        super().__init__(manga_name, base_url)

    def _scrape_manga(self):
        search_results = MangaOwlSearch(self.name).search()
        if not search_results:
            raise MangaDoesNotExist(f"manga {self.name} does not exist")
        manga_url = search_results["1"]["manga_url"]
        print(manga_url)
        manga_html = get_html_from_url(manga_url)
        return manga_html

    def _scrape_volume(self, volume: int):
        manga_html = self._scrape_manga()
        chapter_list = manga_html.find("table", {"class": "table-striped"})
        chapter_list = chapter_list.find_all("a")
        try:
            volume_url = chapter_list[volume - 1].get("href")
        except KeyError:
            raise VolumeDoesntExist(f"manga volume {volume} does not exist")
        return get_html_from_url(volume_url)

    def page_urls(self, volume):
        volume_html = self._scrape_volume(volume)
        items = volume_html.find_all("div", {"class": "item"})
        all_page_urls = [x.find("img").get("data-src") for x in items if x.find("img")]
        return all_page_urls

    # TODO: place in base class, used by mangakaka too
    def page_data(self, page_url: str):
        page_num = Path(page_url).stem
        img_data = requests.get(page_url).content
        return (int(page_num), img_data)

    def all_volume_numbers(self) -> Iterable[int]:
        manga_html = self._scrape_manga()
        chapter_list = manga_html.find("table", {"class": "table-striped"}).find_all(
            "a"
        )
        return [int(chapter.text.split()[1]) for chapter in chapter_list]


class MangaOwlSearch(BaseSearchParser):
    """
    Parses search queries from mangareader.net/search
    """

    def __init__(self, query: str, base_url: str = "http://mangaowl.com") -> None:
        super().__init__(query, base_url)

        self.results: List[Tag] = []

    def _scrape_results(self, page_num=1, last_page=1):
        if page_num > last_page:
            return self.results
        query = re.sub(r"[_-]", " ", self.query)
        url = f"{self.base_url}/search/{query}/{page_num}"
        html_response = get_html_from_url(url)
        navigation = html_response.find("div", {"class": "navigation"})
        if navigation and navigation.find_all("li"):
            pages = []
            for li in navigation.find_all("li"):
                text = li.text.replace("\n", "")
                if text.isdigit():
                    pages.append(text)
            last_page = sorted(pages)[-1]
        results = html_response.find_all("div", {"class": "comicView"})
        if not results:
            logging.warning(f"No search results found for {self.query}")
            # TODO: raise error instead, then catch in __main__ and sys.exit?
            sys.exit()
        self.results += results

        # TODO: split func up
        # TODO: threadpool?
        return self._scrape_results(page_num + 1, int(last_page))

    def _extract_text(self, result: Tag):
        manga_name = result.get("data-title")
        manga_url = result.find("a").get("href")
        chapters_span = result.find("span", {"class": "tray-item"})
        chapters = extract_chapter_number(chapters_span.text)

        return {
            "title": manga_name,
            "manga_url": manga_url,
            "chapters": chapters,
            "type": "-",
        }

    def search(self):
        """
        Extract each mangas metadata from the search results
        """
        results = self._scrape_results()
        metadata: Dict[str, Dict[str, str]] = {}
        for key, result in enumerate(results, start=1):
            try:
                manga_metadata = self._extract_text(result)
                metadata[str(key)] = manga_metadata
            except CannotExtractChapter as e:
                logger.warning(e)
        return metadata


class MangaOwl(BaseSiteParser):
    def __init__(self, manga_name: Optional[str] = None) -> None:
        super().__init__(
            manga_name=manga_name,
            base_url="http://mangaowl.com",
            manga_parser=MangaOwlParser,
            search_parser=MangaOwlSearch,
        )
