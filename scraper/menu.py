from typing import Any, Dict, List, Optional, Type

from tabulate import tabulate

from scraper.exceptions import InvalidOption
from scraper.new_types import SearchResults
from scraper.parsers.types import SiteParser
from scraper.utils import menu_input


class Menu:
    """
    Base class for all menus.
    """

    def __init__(
        self,
        options: Dict[str, str],
        choices: Optional[str] = None,
        parent: Optional["Menu"] = None,
    ) -> None:
        self.parent: Menu = parent
        self.options: Dict[str, str] = self._add_parent_to_options(options)
        self.choices: str = self._add_back_to_choices(choices)

    def handle_options(self) -> Any:
        """
        Extract and execute a method from self.options
        """
        try:
            print(self.choices)
            choice = menu_input()
            item = self.options[choice]
            return item
        except KeyError:
            raise InvalidOption(
                f"{choice} is invalid. Choose an option from "
                f"{', '.join(self.options.keys())}"
            )

    def _add_parent_to_options(self, options: Dict[str, Any]) -> Dict[str, str]:
        """
        Modify options to include parent menu
        """
        if self.parent:
            number_options = len(options)
            new_option_key = str(number_options + 1)
            options[new_option_key] = self.parent
        return options

    def _add_back_to_choices(self, choices: str) -> str:
        """
        Modify choices to include back option to parent menu
        """
        if not self.parent:
            return choices
        num = len(self.options)
        if choices:
            return f"{choices}\n{num}. Back"
        else:
            return f"{num}. Back"

    @classmethod
    def from_list(cls, l: List[str]) -> "Menu":
        """
        Constructs self._options and self.choices from a list.
        """
        options = {str(k + 1): i for k, i in enumerate(l)}
        choices = "\n".join("{}. {}".format(k, i) for k, i in sorted(options.items()))
        return cls(options, choices)


class SearchMenu(Menu):
    def __init__(self, query: List[str], parser: Type[SiteParser]) -> None:
        self.parser: SiteParser = parser()
        self.search_results: SearchResults = self._search(query)
        choices: str = self.table()
        options: Dict[str, str] = self._create_options()
        Menu.__init__(self, options, choices)

    def _search(self, query: List[str]) -> SearchResults:
        """
        Search for query and return Search object
        """
        search_results = self.parser.search(" ".join(query))
        return search_results

    def table(self) -> str:
        # TODO: apply maximum restriction for title length
        columns = ["", "Title", "Volumes", "Source"]
        data = [
            [k, x["title"], x["chapters"], x["source"]]
            for k, x in self.search_results.items()
        ]
        table = tabulate(data, headers=columns, tablefmt="psql")
        return table

    def _create_options(self) -> Dict[str, str]:
        """
        Take number and url from search object
        """
        return {k: v["manga_url"] for k, v in self.search_results.items()}
