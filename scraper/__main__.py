import argparse
import logging
import sys
from typing import List, Tuple

from scraper.download import download_manga
from scraper.exceptions import MangaDoesNotExist

# from scraper.gui import AppGui
from scraper.menu import SearchMenu
from scraper.parsers.mangareader import MangaReader
from scraper.parsers.types import SiteParserClass
from scraper.uploaders import upload
from scraper.utils import settings

# PyQt5 is broken, requires to install PyQt5-sip then PyQt5
# however there is no way to specify install order in setup.py
# so this nasty hack will have to do now
# from PyQt5.QtWidgets import QApplication


MANGA_DIR = settings()["config"]["manga_directory"]
SOURCE = settings()["config"]["source"]


logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    format="%(message)s",
)


logger = logging.getLogger(__name__)


# TODO: fix broken gui
# def gui() -> None:
#     app = QApplication(sys.argv)
#     window = AppGui()
#     window.show()
#     sys.exit(app.exec_())


def get_volume_values(volume: str) -> List[int]:
    """
    Transform a string digit into a list of integers
    """
    if "-" in volume:
        start, end = volume.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(x) for x in volume.split()]


def manga_search(query: List[str], parser: SiteParserClass) -> Tuple[str, List[str]]:
    """
    Search for a manga and return the manga name and volumes
    selected by user input
    """
    menu = SearchMenu(query, parser)
    manga = menu.handle_options()
    msg = (
        "Which volume(s) do you want to download "
        "(Enter alone to download all volumes)?\n>> "
    )
    volumes = input(msg)
    return (manga.strip(), volumes.split())


def get_manga_parser(source: str) -> SiteParserClass:
    """
    Use the string to return correct parser class
    """
    sources = {"mangareader": MangaReader}
    parser = sources.get(source)
    if not parser:
        raise ValueError(f"{source} is not supported try {', '.join(sources.keys())}")
    return parser


def cli(arguments: List[str]) -> dict:
    parser = get_parser()
    args = vars(parser.parse_args(arguments))
    filetype = "cbz" if args["cbz"] else "pdf"
    manga_parser = get_manga_parser(args["source"])

    if args["search"]:
        args["manga"], args["volumes"] = manga_search(args["search"], manga_parser)

    else:
        args["manga"] = " ".join(args["manga"])

    if args["volumes"]:
        volumes: List[int] = []
        for vol in args["volumes"]:
            volumes += get_volume_values(vol)
        args["volumes"] = volumes
    else:
        args["volumes"] = None

    try:
        manga = download_manga(
            manga_name=args["manga"],
            volumes=args["volumes"],
            filetype=filetype,
            parser=manga_parser,
        )
    except MangaDoesNotExist:
        logging.info(
            f"No manga found for {args['manga']}. Searching for closest match."
        )
        return cli(["--search", args["manga"]])

    if args["upload"]:
        upload(manga, args["upload"])

    return args


def cli_entry() -> None:
    """
    Required as entry_point in setup.py cannot take args,
    however, we need cli() to take args for unit testing
    purposes. Hence the need for this function.
    """
    cli(sys.argv[1:])


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="downloads and converts manga volumes to pdf or cbz format"
    )
    parser.add_argument("--manga", "-m", type=str, help="manga series name", nargs="*")
    parser.add_argument(
        "--search", "-s", type=str, help="search manga reader", nargs="*"
    )
    parser.add_argument(
        "--volumes", "-v", nargs="+", type=str, help="manga volume to download"
    )
    parser.add_argument("--output", "-o", default=MANGA_DIR)
    parser.add_argument(
        "--cbz", action="store_true", help="output in cbz format instead of pdf"
    )
    parser.add_argument(
        "--source", "-z", type=str, choices={"mangareader"}, default=SOURCE
    )
    parser.add_argument("--upload", "-u", type=str, choices={"dropbox", "mega"})
    return parser


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_entry()
    # else:
    #     gui()
