''' Concatenates jpgs that correspond to mangas volume and outputs as a PDF file.'''
from config import JPG_DIR, MANGA_DIR
from jpg2pdf import find_volume, get_volume_pages
import os
import zipfile


def make_cbz(cbz_filename, list_pages):
    ''' Construct a CBZ from a list of sorted images.'''
    cbz_dirname = '.'.join(os.path.basename(cbz_filename).split('.')[:-1])
    with zipfile.ZipFile(cbz_filename, 'w') as cbz:
        for page in list_pages:
            # can't just use the filename here as the ordering of pages in the CBZ comes from the lexical sort order of their filenames
            # so we'll just pad the page number segment out to like 6 digits
            pnparts = os.path.basename(page).split('.')[0].split('_')
            arcname = os.path.join(cbz_dirname, '{}_{}_{:06d}.jpg'.format(pnparts[0], pnparts[1], int(pnparts[2], 10)))
            cbz.write(page, arcname)

    print("Created {}".format(cbz_filename))


def create_volume(manga, volume, out_dir):
    ''' Construct a CBZ for a given volume.'''
    sorted_volume_pages = get_volume_pages(volume)
    # volume_name = manga+'_volume_'+str(volume)
    volume_name = '{}_volume_{:02d}'.format(manga, int(volume, 10))
    volume_filename = os.path.join(out_dir, '{}.cbz'.format(volume_name))
    make_cbz(volume_filename, sorted_volume_pages)


def create_all_volumes(manga, out_dir):
    ''' Construct a CBZ for every volume.'''
    volumes = set([x.split("_")[1] for x in os.listdir(JPG_DIR)])
    for volume in sorted(volumes):
        create_volume(manga, volume, out_dir)


def create_manga_cbz(manga, volume=None, out_dir=MANGA_DIR):
    ''' Createa  CBZ for a single or all manga volumes.'''
    out_dir = os.path.join(out_dir, manga.split("_")[0])
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if not volume:
        create_all_volumes(manga, out_dir)

    else:
        create_volume(manga, volume, out_dir)
