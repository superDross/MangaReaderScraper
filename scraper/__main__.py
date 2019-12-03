import argparse
import logging
import os
import sys

from scraper.config import JPG_DIR, MANGA_DIR
from scraper.converter import convert
from scraper.download import download_manga
from scraper.menu import SearchMenu

try:
    # PyQt5 is broken, requires to install PyQt5-sip then PyQt5
    # however there is no way to specify install order in setup.py
    # so this nasty hack will have to do now
    from PyQt5.QtWidgets import QApplication
    from scraper.gui import AppGui
except:
    pass


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


def cli() -> None:
    parser = get_parser()
    args = vars(parser.parse_args())

    if args["search"]:
        menu = SearchMenu(args["search"])
        args["manga"] = menu.handle_options()
        msg = "Which volume do you want to download (Enter alone to download all volumes)?\n"
        args["volume"] = input(msg)
        args["volume"] = None if args["volume"] == "" else args["volume"]

    download_manga(args["manga"], args["volume"])
    convert(args["manga"], args["volume"], args["cbz"])
    clean_up()


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="downloads and converts manga volumes to pdf or cbz format"
    )
    parser.add_argument("--manga", "-m", type=str, help="manga series name")
    parser.add_argument(
        "--search", "-s", type=str, help="search manga reader", nargs="*"
    )
    parser.add_argument("--volume", "-v", type=int, help="manga volume to download")
    parser.add_argument("--output", "-o", default=MANGA_DIR)
    parser.add_argument(
        "--cbz", action="store_true", help="output in cbz format instead of pdf"
    )
    return parser


def clean_up() -> None:
    """ Delete all scrapped jpg files."""
    directory = JPG_DIR
    for jpg in os.listdir(directory):
        # os.remove(os.path.join(directory, jpg))
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        gui()
