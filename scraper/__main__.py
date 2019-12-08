import argparse
import logging
import os
import sys
from typing import Optional, Union

from scraper.download import Download
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


def download_manga(manga_name: str, volume: Optional[int], filetype: str) -> None:
    downloader = Download(manga_name, filetype)
    downloader.download_volumes(volume)


def cli() -> None:
    parser = get_parser()
    args = vars(parser.parse_args())

    if args["search"]:
        menu = SearchMenu(args["search"])
        args["manga"] = menu.handle_options()
        msg = "Which volume do you want to download (Enter alone to download all volumes)?\n"
        volume = input(msg)
        if "-" in volume:
            start, end = volume.split("-")
            args["volumes"] = list(range(int(start), int(end) + 1))
        elif volume:
            args["volumes"] = [int(x) for x in volume.split()]
        else:
            args["volumes"] = None

    filetype = "cbz" if args["cbz"] else "pdf"

    download_manga(args["manga"], args["volumes"], filetype)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="downloads and converts manga volumes to pdf or cbz format"
    )
    parser.add_argument("--manga", "-m", type=str, help="manga series name")
    parser.add_argument(
        "--search", "-s", type=str, help="search manga reader", nargs="*"
    )
    parser.add_argument(
        "--volumes", "-v", nargs="+", type=int, help="manga volume to download"
    )
    parser.add_argument("--output", "-o", default=MANGA_DIR)
    parser.add_argument(
        "--cbz", action="store_true", help="output in cbz format instead of pdf"
    )
    return parser


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        gui()
