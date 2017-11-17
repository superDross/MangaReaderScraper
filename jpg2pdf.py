''' Organise and costruct FFXII PDF manga volumes from jpeg pages.'''
from fpdf import FPDF
from PIL import Image
import itertools
import os
import re

HERE = os.path.dirname(os.path.realpath(__file__))


def get_volume_pages(desired_volume, directory=None):
    ''' Sort and return a list of all jpgs of a specfic manga volume.'''
    if not directory:
        directory = HERE+'/jpgs/'
    files = [x for x in os.listdir(directory) if x.endswith('jpg')]
    volume_jpgs = []
    for jpg in files:
        volume, index = find_volume(jpg)
        if int(volume) == int(desired_volume):
            volume_jpgs.append(jpg)
    sort_by_volume = lambda x: int(re.split(r'[_.]', x)[index+1])
    sorted_volume = sorted(volume_jpgs, key=sort_by_volume)
    fully_sorted_volume = [directory+x for x in sorted_volume]
    return fully_sorted_volume


def find_volume(filename):
    ''' Find and return the volume number of a given manga filename.'''
    for index, split_file in enumerate(filename.split("_")):
        if split_file.isdigit():
            return split_file, index


def make_pdf(pdf_filename, list_pages):
    ''' Construct a PDF from a list of sorted images.'''
    cover = Image.open(list_pages[0])
    width, height = cover.size
    pdf = FPDF(unit='pt', format=[width, height])
    for page in list_pages:
        pdf.add_page()
        pdf.image(str(page), 0, 0)
    pdf.output(pdf_filename, 'F')
    print('Created {}'.format(pdf_filename))


def create_all_volumes(manga, out_dir):
    ''' Construct a PDF for every volume '''
    out_dir = HERE+'/mangas/'
    volumes = set([x.split("_")[1] for x in os.listdir(HERE+'/jpgs/')])
    for volume in sorted(volumes):
        create_volume(manga, volume, out_dir)


def create_volume(manga, volume, out_dir):
    ''' Construct a PDF for a given volume.'''
    sorted_volume_pages = get_volume_pages(volume)
    volume_name = out_dir+manga+'_volume_'+str(volume)
    make_pdf(volume_name+".pdf", sorted_volume_pages)
