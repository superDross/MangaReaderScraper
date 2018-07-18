from config import JPG_DIR, MANGA_DIR
import download
import jpg2pdf
import jpg2cbz
import search
import argparse
import os


def cli():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['search']:
        args['manga'] = search.search_and_get_link(args['search'])
        msg = 'Which volume do you want to download (Enter alone to download all volumes)?\n'
        args['volume'] = input(msg)
        args['volume'] = None if args['volume'] == '' else args['volume']

    download.download_manga(args['manga'], args['volume'])

    if args['cbz']:
        jpg2cbz.create_manga_cbz(args['manga'], args['volume'], args['output'])
    else:
        jpg2pdf.create_manga_pdf(args['manga'], args['volume'], args['output'])

    clean_up()


def get_parser():
    parser = argparse.ArgumentParser(description='downloads and converts manga volumes to pdf or cbz format')
    parser.add_argument('--manga', '-m', type=str, help='manga series name')
    parser.add_argument('--search', '-s', type=str, help='search manga reader', nargs='*')
    parser.add_argument('--volume', '-v', type=int, help='manga volume to download')
    parser.add_argument('--output', '-o', default=MANGA_DIR)
    parser.add_argument('--cbz', action='store_true', help='output in cbz format instead of pdf')
    return parser


def clean_up():
    ''' Delete all scrapped jpg files.'''
    directory = JPG_DIR
    for jpg in os.listdir(directory):
        os.remove(os.path.join(directory, jpg))


if __name__ == '__main__':
    cli()
