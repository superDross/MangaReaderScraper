import argparse
import logging
import sys
from typing import Dict, List, Optional, Tuple, Type

from scraper.download import Download
from scraper.exceptions import MangaDoesNotExist
from scraper.manga import Manga
from scraper.menu import SearchMenu
from scraper.parsers.mangakaka import MangaKaka
from scraper.parsers.mangareader import MangaReader
from scraper.parsers.types import SiteParserClass
from scraper.uploaders.types import Uploader
from scraper.uploaders.uploaders import DropboxUploader, MegaUploader, PcloudUploader
from scraper.utils import menu_input, settings

CONFIG = settings()["config"]

logging.basicConfig(
    level=logging.INFO, format="%(message)s",
)


logger = logging.getLogger(__name__)


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
        "(Enter alone to download all volumes)?"
    )
    volumes = menu_input(msg)
    return (manga.strip(), volumes.split())


def get_manga_parser(source: str) -> SiteParserClass:
    """
    Use the string to return correct parser class
    """
    sources: Dict[str, SiteParserClass] = {
        "mangareader": MangaReader,
        "mangakaka": MangaKaka,
    }
    parser = sources.get(source)
    if not parser:
        raise ValueError(f"{source} is not supported try {', '.join(sources.keys())}")
    return parser


def download_manga(
    manga_name: str,
    volumes: Optional[int],
    filetype: str,
    parser: SiteParserClass,
    preferred_name: Optional[str] = None,
) -> Manga:
    downloader = Download(manga_name, filetype, parser)
    manga = downloader.download_volumes(volumes, preferred_name)
    return manga


def upload(manga: Manga, service: str) -> Uploader:
    services: Dict[str, Type[Uploader]] = {
        "dropbox": DropboxUploader,
        "mega": MegaUploader,
        "pcloud": PcloudUploader,
    }
    uploader = services[service]()
    return uploader(manga)


def cli(arguments: List[str]) -> dict:
    parser = get_parser()
    args = vars(parser.parse_args(arguments))
    manga_parser = get_manga_parser(args["source"])

    if args["remove"] and not args["upload"]:
        raise IOError("Cannot use --remove without --upload")

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
            filetype=args["filetype"],
            parser=manga_parser,
            preferred_name=args["override_name"],
        )
    except MangaDoesNotExist:
        logging.info(
            f"No manga found for {args['manga']}. Searching for closest match."
        )
        updated_args = change_args_to_search(args)
        return cli(updated_args)

    if args["upload"]:
        upload(manga, args["upload"])

    if args["remove"]:
        for volume in manga.volumes:
            volume.file_path.unlink()

    return args


def change_args_to_search(args: Dict[str, Optional[str]]) -> List[Optional[str]]:
    """
    Alters arguments to use --search
    """
    updated_args = []
    args.update({"manga": None, "volumes": None, "search": args["manga"]})

    flags = ["remove"]

    for k, v in args.items():
        if (k == "upload" and not v) or (k in flags and v is False):
            continue
        if k in flags and v is True:
            updated_args.append(f"--{k}")
            continue
        updated_args.append(f"--{k}")
        updated_args.append(v)
    return updated_args


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
    parser.add_argument("--output", "-o", default=CONFIG["manga_directory"])
    parser.add_argument(
        "--filetype",
        "-f",
        type=str,
        choices={"pdf", "cbz"},
        default=CONFIG["filetype"],
        help="format to store manga as",
    )
    parser.add_argument(
        "--source",
        "-z",
        type=str,
        choices={"mangareader", "mangakaka"},
        default=CONFIG["source"],
        help="website to scrape data from",
    )
    parser.add_argument(
        "--upload",
        "-u",
        type=str,
        choices={"dropbox", "mega", "pcloud"},
        help="upload manga to a cloud storage service",
    )
    parser.add_argument(
        "--override_name",
        "-n",
        type=str,
        help="change manga name for all saved/uploaded files",
    )
    parser.add_argument(
        "--remove",
        "-r",
        action="store_true",
        help="delete downloaded volumes aftering uploading to a cloud service",
    )
    return parser


if __name__ == "__main__":
    cli_entry()
