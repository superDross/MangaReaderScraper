import re
from typing import Dict, List

from tabulate import tabulate


class TableProducer:
    """
    Search results table
    """

    def __init__(self) -> None:
        self.results: Dict[str, Dict[str, str]] = {}
        self.table: str = None

    def _extract_text(self, result: str) -> Dict[str, str]:
        """
        Extract the desired text from a HTML search result
        """
        manga_name = result.find("div", {"class": "manga_name"})
        title = manga_name.text
        manga_url = manga_name.find("a").get("href")
        chapters = result.find("div", {"class": "chapter_count"}).text
        manga_type = result.find("div", {"class": "manga_type"}).text
        return {
            "title": title.replace("\n", ""),
            "manga_url": manga_url[1:],
            "chapters": re.sub(r"\D", "", chapters),
            "type": manga_type.split("(")[0],
        }

    def _extract_metadata(self, search_results: List[str]) -> None:
        """
        Extract all the desired text from the HTML search
        results and set as a dict.
        """
        for key, result in enumerate(search_results, start=1):
            manga_metadata = self._extract_text(result)
            self.results[str(key)] = manga_metadata

    def _to_table(self) -> None:
        """
        Transform the dictionary into a table
        """
        columns = ["", "Title", "Volumes", "Type"]
        data = [
            [k, x["title"], x["chapters"], x["type"]] for k, x in self.results.items()
        ]
        table = tabulate(data, headers=columns, tablefmt="psql")
        self.table = table

    def generate(self, search_results: List[str]) -> str:
        """
        Generate search results into a table
        """
        self._extract_metadata(search_results)
        self._to_table()
        return self.table
