from pathlib import Path
from unittest import mock

from bs4 import BeautifulSoup
from scraper.parsers.base import BaseSiteParser

# used as a mocked output for MangaReaderSearch.metadata()
METADATA = {
    "1": {
        "chapters": "3",
        "manga_url": "dragon-ball-episode-of-bardock",
        "source": "mangareader",
        "title": "Dragon Ball: Episode of Bardock",
    },
    "2": {
        "chapters": "35",
        "manga_url": "dragon-ball-sd",
        "source": "mangareader",
        "title": "Dragon Ball SD",
    },
    "3": {
        "chapters": "4",
        "manga_url": "dragonball-next-gen",
        "source": "mangareader",
        "title": "DragonBall Next Gen",
    },
    "4": {
        "chapters": "520",
        "manga_url": "dragon-ball",
        "source": "mangareader",
        "title": "Dragon Ball",
    },
    "5": {
        "chapters": "3",
        "manga_url": "dragon-ball-z-rebirth-of-f",
        "source": "mangareader",
        "title": "Dragon Ball Z - Rebirth of F",
    },
    "6": {
        "chapters": "62",
        "manga_url": "dragon-ball-super",
        "source": "mangareader",
        "title": "Dragon Ball Super",
    },
}


TABLE = (
    "+----+---------------------------------+-----------+-------------+\n"
    "|    | Title                           |   Volumes | Source      |\n"
    "|----+---------------------------------+-----------+-------------|\n"
    "|  1 | Dragon Ball: Episode of Bardock |         3 | mangareader |\n"
    "|  2 | Dragon Ball SD                  |        35 | mangareader |\n"
    "|  3 | DragonBall Next Gen             |         4 | mangareader |\n"
    "|  4 | Dragon Ball                     |       520 | mangareader |\n"
    "|  5 | Dragon Ball Z - Rebirth of F    |         3 | mangareader |\n"
    "|  6 | Dragon Ball Super               |        62 | mangareader |\n"
    "+----+---------------------------------+-----------+-------------+"
)


class MockedImgResponse:
    """
    Returns a mocked response with manga img as content
    """

    def __init__(self):
        with open("tests/test_files/jpgs/test-manga_1_1.jpg", "rb") as f:
            self.content = f.read()


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


class MockedPyCloud:
    listed = {"error": True, "result": 2005}

    def __init__(self, *args, **kwargs):
        pass

    def createfolder(self, *args, **kwargs):
        return {"result": 0, "metadata": "path"}

    def listfolder(self, *args, **kwargs):
        return self.listed

    def uploadfile(self, *args, **kwargs):
        return {"status": "success"}


class MockedPyCloudFail(MockedPyCloud):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def createfolder(self, *args, **kwargs):
        return {"error": "directory already exists"}

    def uploadfile(self, *args, **kwargs):
        return {"error": "something happened"}


class MockedMega:
    def __init__(self, *args, **kwargs):
        self.found = ["start", "finish"]

    def login(self, *args, **kwargs):
        return self

    def find(self, *args, **kwargs):
        return self.found

    def create_folder(self, *args, **kwargs):
        return {"dir": "one", "subdir": "two"}

    def upload(self, *args, **kwargs):
        return {"status": "success"}


class MockedMegaNotFound(MockedMega):
    """
    Causes self.find to return False
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.found = False


class MockedDropbox:
    def __init__(self, *args, **kwargs):
        self.match_found = True
        self.file = "/non-existing/file.txt"

    def files_search(self, *args, **kwargs):
        searcher = mock.MagicMock()
        searcher.matches = self.match_found
        return searcher

    def files_upload(self, *args, **kwargs):
        response = mock.MagicMock()
        response.path_lower = self.file
        response.text = "success"
        return response


class MockedDropboxRealFile(MockedDropbox):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.match_found = False
        self.file = "tests/test_files/mangakaka/dragonball_super_page.html"


def setup_uploader(uploader):
    upl = uploader()
    manga = mock.MagicMock()
    manga.name = mock.Mock(return_value="hiya")
    upl._setup_adapter(manga)
    return upl


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
