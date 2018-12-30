import argparse
import logging
import os

import download
import converter
import search
from menu import SearchMenu
from config import JPG_DIR, MANGA_DIR


logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    format='%(message)s'
)


logger = logging.getLogger(__name__)


def download_manga(manga, volume):
    downloader = download.DownloadManga(manga)
    if not os.path.exists(JPG_DIR):
        os.makedirs(JPG_DIR)
    if volume:
        downloader.download_volume(volume)
    else:
        downloader.download_all_volumes()

def convert(manga, volume, cbz):
    conversion = converter.Conversion(manga)
    conversion.type = 'cbz' if cbz else 'pdf'
    if not os.path.exists(MANGA_DIR):
        os.makedirs(MANGA_DIR)
    if volume:
        conversion.convert_volume(volume)
    else:
        conversion.convert_all_volumes()

def cli():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['search']:
        menu = SearchMenu(args['search'])
        args['manga'] = menu.handle_options()
        msg = 'Which volume do you want to download (Enter alone to download all volumes)?\n'
        args['volume'] = input(msg)
        args['volume'] = None if args['volume'] == '' else args['volume']

    download_manga(args['manga'], args['volume'])
    convert(args['manga'], args['volume'], args['cbz'])
    clean_up()


def get_parser():
    parser = argparse.ArgumentParser(
        description='downloads and converts manga volumes to pdf or cbz format')
    parser.add_argument('--manga', '-m', type=str, help='manga series name')
    parser.add_argument('--search', '-s', type=str,
                        help='search manga reader', nargs='*')
    parser.add_argument('--volume', '-v', type=int,
                        help='manga volume to download')
    parser.add_argument('--output', '-o', default=MANGA_DIR)
    parser.add_argument('--cbz', action='store_true',
                        help='output in cbz format instead of pdf')
    return parser


def clean_up():
    ''' Delete all scrapped jpg files.'''
    directory = JPG_DIR
    for jpg in os.listdir(directory):
        os.remove(os.path.join(directory, jpg))


if __name__ == '__main__':
    cli()
