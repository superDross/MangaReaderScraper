from typing import Dict, Optional

from tabulate import tabulate

from scraper.new_types import SearchResults


# TODO: this should now be a function and not a class


class TableProducer:
    """
    Search results table
    """

    def __init__(self) -> None:
        self.results: Dict[str, Dict[str, str]] = {}
        self.table: Optional[str] = None

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

    def generate(self, search_results: SearchResults) -> Optional[str]:
        """
        Generate search results into a table
        """
        self.results = search_results
        self._to_table()
        return self.table
