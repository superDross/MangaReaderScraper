import manga_download
import jpg2pdf
import argparse
import os

HERE = os.path.dirname(os.path.realpath(__file__))


def cli():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['volume']:
        manga_download.download_volume(args['manga'], args['volume'])
        jpg2pdf.create_volume(args['manga'], args['volume'], args['output'])
    else:
        manga_download.download_all_volumes(args['manga'])
        jpg2pdf.create_all_volumes(args['manga'], args['output'])


def get_parser():
    parser = argparse.ArgumentParser(description='downloads and converts manga volumes to pdf format')
    parser.add_argument('--manga', '-m', type=str, help='manga series name', required=True)
    parser.add_argument('--volume', '-v', type=int, help='manga volume to download')
    parser.add_argument('--output', '-o', default=HERE+'/mangas/')
    return parser


if __name__ == '__main__':
    cli()
