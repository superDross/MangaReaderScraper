from config import HERE
import download
import jpg2pdf
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
    jpg2pdf.create_manga_pdf(args['manga'], args['volume'], args['output'])
    clean_up()


def get_parser():
    parser = argparse.ArgumentParser(description='downloads and converts manga volumes to pdf format')
    parser.add_argument('--manga', '-m', type=str, help='manga series name')
    parser.add_argument('--search', '-s', type=str, help='search manga reader', nargs='*')
    parser.add_argument('--volume', '-v', type=int, help='manga volume to download')
    parser.add_argument('--output', '-o', default=HERE+'/mangas/')
    return parser


def clean_up():
    ''' Delete all scrapped jpg files.'''
    directory = HERE+'/jpgs/'
    for jpg in os.listdir(directory):
        os.remove(directory+jpg)


if __name__ == '__main__':
    cli()
