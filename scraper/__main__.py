import argparse
import logging
import sys
from typing import List, Tuple, Union

from scraper.download import download_manga
from scraper.menu import SearchMenu
from scraper.utils import settings

try:
    # PyQt5 is broken, requires to install PyQt5-sip then PyQt5
    # however there is no way to specify install order in setup.py
    # so this nasty hack will have to do now
    from PyQt5.QtWidgets import QApplication
    from scraper.gui import AppGui
except:
    pass

MANGA_DIR = settings()["manga_directory"]


logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    format="%(message)s",
)


logger = logging.getLogger(__name__)


def gui() -> None:
    app = QApplication(sys.argv)
    ex = AppGui()
    sys.exit(app.exec_())


def get_volume_values(volume: str) -> Union[List[int], None]:
    """
    Transform a string digit into a list of integers
    """
    if "-" in volume:
        start, end = volume.split("-")
        return list(range(int(start), int(end) + 1))
    elif volume:
        return [int(x) for x in volume.split()]
    else:
        return None


def manga_search(query: str) -> Tuple[str, List[int]]:
    """
    Search for a manga and return the manga name and volumes
    selected by user input
    """
    menu = SearchMenu(query)
    manga = menu.handle_options()
    msg = (
        "Which volume do you want to download "
        "(Enter alone to download all volumes)?\n>> "
    )
    volume_input = input(msg)
    volumes = get_volume_values(volume_input)
    return (manga, volumes)


def cli(arguments: List[str]) -> dict:
    parser = get_parser()
    args = vars(parser.parse_args(arguments))
    filetype = "cbz" if args["cbz"] else "pdf"

    if args["search"]:
        args["manga"], args["volumes"] = manga_search(args["search"])

    elif args["volumes"]:
        volumes = []
        for vol in args["volumes"]:
            volumes += get_volume_values(vol)
        args["volumes"] = volumes

    download_manga(args["manga"], args["volumes"], filetype)
    return args


def cli_entry() -> None:
    """
    Required as entry_point in setup.py cannot take args,
    however, we need cli() to take args for unit testing
    purposes. Hence the need for this funcion.
    """
    cli(sys.argv[1:])


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="downloads and converts manga volumes to pdf or cbz format"
    )
    parser.add_argument("--manga", "-m", type=str, help="manga series name")
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
    return parser


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_entry()
    else:
        gui()
