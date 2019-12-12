from unittest import mock

import pytest

from scraper.exceptions import InvalidOption
from scraper.menu import Menu, SearchMenu


def test_searchmenu_attributes(search_html):
    search_results = search_html.find_all("div", {"class": "mangaresultitem"})
    with mock.patch("scraper.menu.get_search_results") as mocked_func:
        mocked_func.return_value = search_results
        search_menu = SearchMenu("dragon-ball")
        expected_choices = (
            "+----+---------------------------------+-----------+--------+\n"
            "|    | Title                           |   Volumes | Type   |\n"
            "|----+---------------------------------+-----------+--------|\n"
            "|  1 | Dragon Ball                     |       520 | Manga  |\n"
            "|  2 | Dragon Ball SD                  |        34 | Manga  |\n"
            "|  3 | Dragon Ball: Episode of Bardock |         3 | Manga  |\n"
            "|  4 | DragonBall Next Gen             |         4 | Manga  |\n"
            "|  5 | Dragon Ball Z - Rebirth of F    |         3 | Manga  |\n"
            "|  6 | Dragon Ball Super               |        54 | Manga  |\n"
            "+----+---------------------------------+-----------+--------+"
        )
        exepected_options = {
            "1": "dragon-ball",
            "2": "dragon-ball-sd",
            "3": "dragon-ball-episode-of-bardock",
            "4": "dragonball-next-gen",
            "5": "dragon-ball-z-rebirth-of-f",
            "6": "dragon-ball-super",
        }
        assert search_menu.choices == expected_choices
        assert search_menu.options == exepected_options


@pytest.mark.parametrize(
    "selected,expected", [("1", "dragon-ball"), ("6", "dragon-ball-super")]
)
def test_menu_options(selected, expected, monkeypatch, menu):
    monkeypatch.setattr("builtins.input", lambda x: selected)
    requested = menu.handle_options()
    assert requested == expected


def test_invalid_choic(monkeypatch, menu):
    monkeypatch.setattr("builtins.input", lambda x: "999")
    with pytest.raises(InvalidOption):
        menu.handle_options()


def test_parent_menu(monkeypatch, menu):
    assert menu.options["7"] == menu.parent
    monkeypatch.setattr("builtins.input", lambda x: "7")
    requested = menu.handle_options()
    assert requested == menu.parent


def test_init_from_list():
    menu = Menu.from_list(["a", "b", "c"])
    assert menu.options == {"1": "a", "2": "b", "3": "c"}
    assert menu.choices == "1. a\n2. b\n3. c"


def test_back_button(menu_no_choices):
    back_button = menu_no_choices.options.get("3")
    assert back_button == menu_no_choices.parent
