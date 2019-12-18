from pathlib import Path

from bs4 import BeautifulSoup

from scraper.parsers.base import BaseSiteParser

# used as a mocked output for MangaReaderSearch.metadata()
METADATA = {
    "1": {
        "title": "Dragon Ball",
        "manga_url": "dragon-ball",
        "chapters": "520",
        "type": "Manga ",
    },
    "2": {
        "title": "Dragon Ball SD",
        "manga_url": "dragon-ball-sd",
        "chapters": "34",
        "type": "Manga ",
    },
    "3": {
        "title": "Dragon Ball: Episode of Bardock",
        "manga_url": "dragon-ball-episode-of-bardock",
        "chapters": "3",
        "type": "Manga ",
    },
    "4": {
        "title": "DragonBall Next Gen",
        "manga_url": "dragonball-next-gen",
        "chapters": "4",
        "type": "Manga ",
    },
    "5": {
        "title": "Dragon Ball Z - Rebirth of F",
        "manga_url": "dragon-ball-z-rebirth-of-f",
        "chapters": "3",
        "type": "Manga ",
    },
    "6": {
        "title": "Dragon Ball Super",
        "manga_url": "dragon-ball-super",
        "chapters": "54",
        "type": "Manga ",
    },
}


TABLE = (
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


class MockedMangaReaderParser:
    """
    Mocks MangaReaderMangaParser

    Can't use MagicMock as it results in a pickling error when used with
    multiprocessig, hence the need for this hack.
    """

    def __init__(self, manga_name, base_url="www.nothing.com"):
        self.name = manga_name
        self.base_url = base_url

    def all_volume_numbers(self):
        return [1, 2, 3]

    def page_urls(self, volume):
        return [
            f"http://mangareader.net/dragon-ball-episode-of-bardock/{volume}",
            f"http://mangareader.net/dragon-ball-episode-of-bardock/{volume}/2",
        ]

    def page_data(self, page_url):
        volume_num, page_num = page_url.split("/")[-2:]
        if not volume_num.isdigit():
            page_num = "1"
        img = open(f"tests/test_files/jpgs/test-manga_1_{page_num}.jpg", "rb").read()
        return (int(page_num), img)


class MockedSearch:
    """
    Mocks SearchParser
    """

    def __init__(self, *args, **kwargs):
        pass

    def search(*args):
        return METADATA


class MockedSiteParser(BaseSiteParser):
    """
    A poor mock of the MangaReaderSiteParser
    """

    def __init__(self, manga_name="dragon-ball"):
        super().__init__(
            manga_name=manga_name,
            base_url="www.nothing.com",
            manga_parser=MockedMangaReaderParser,
            search_parser=MockedSearch,
        )


def get_bs4_tree(filepath):
    html_string = Path(filepath).read_text()
    html = BeautifulSoup(html_string, features="lxml")
    return html


def get_images():
    """
    Opens a list of two jpeg images
    """
    return [
        Path(f"tests/test_files/jpgs/test-manga_1_{n}.jpg").read_bytes() for n in [1, 2]
    ]
