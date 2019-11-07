import re
from typing import List

from tabulate import tabulate

from config import MANGA_URL
from utils import get_html_from_url


class Search:
    def __init__(self):
        self.results: dict = {}
        self.table: str = None

    def _get_search_results(
        self,
        query: str,
        manga_type: int = 0,
        manga_status: int = 0,
        order: int = 0,
        genre: str = "0000000000000000000000000000000000000",
    ) -> List[str]:
        """ Scrape and return HTML dict with search results."""
        url = f"""{MANGA_URL}/search/?w={query}&rd={manga_type}
                   &status={manga_status}&order=0&genre={genre}&p=0"""
        html_response = get_html_from_url(url)
        search_results = html_response.find_all("div", {"class": "mangaresultitem"})
        return search_results

    def _extract_text(self, result: str) -> dict:
        """ Extract the desired text from a HTML search result."""
        manga_name = result.find("div", {"class": "manga_name"})
        title = manga_name.text
        manga_url = manga_name.find("a").get("href")
        chapters = result.find("div", {"class": "chapter_count"}).text
        manga_type = result.find("div", {"class": "manga_type"}).text
        return {
            "title": title.replace("\n", ""),
            "manga_url": manga_url[1:],
            "chapters": re.sub("\D", "", chapters),
            "type": manga_type.split("(")[0],
        }

    def _extract_metadata(self, search_results: List[str]) -> None:
        """ Extract all the desired text from the HTML search
            results and set as a dict.
        """
        key = 1
        for result in search_results:
            manga_metadata = self._extract_text(result)
            self.results[str(key)] = manga_metadata
            key += 1

    def _to_table(self) -> None:
        """ Transform the dictionary into a table."""
        columns = ["", "Title", "Volumes", "Type"]
        data = [
            [k, x["title"], x["chapters"], x["type"]] for k, x in self.results.items()
        ]
        table = tabulate(data, headers=columns, tablefmt="psql")
        self.table = table

    def search(self, query: str) -> None:
        results = self._get_search_results(query)
        self._extract_metadata(results)
        self._to_table()
