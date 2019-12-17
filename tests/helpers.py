from pathlib import Path

from bs4 import BeautifulSoup

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


class MockedMangaReaderParser:
    """
    Mocks MangaReaderParser

    Can't use MagicMock as it results in a pickling error when used with
    multiprocessig, hence the need for this hack.
    """

    def __init__(self, manga_name):
        self.manga_name = manga_name

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
