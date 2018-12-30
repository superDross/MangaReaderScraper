''' Converts manga volume(s) images to a pdf or cbz file.'''
import os
import re
import zipfile
import logging

from fpdf import FPDF
from PIL import Image

from config import JPG_DIR, MANGA_DIR

logger = logging.getLogger(__name__)


class Conversion:
    def __init__(self, manga):
        self.manga = manga
        self.volume = None
        self.images = []
        self._type = 'pdf'
        self.filename = None

    @property
    def type(self):
        ''' Describes file type to convert to.'''
        return self._type

    @type.setter
    def type(self, file_type):
        accepted = ['pdf', 'cbz']
        if file_type not in accepted:
            raise ValueError(f'{file_type} not accepted. '
                             f'Must be in {accepted}')
        self._type = file_type

    def _get_volume_images(self):
        ''' Sort and return a list of all images of a specfic manga volume.'''
        for jpg in os.listdir(JPG_DIR):
            if jpg.endswith('jpg') and self.manga in jpg:
                volume = jpg.split('_')[1]
                if int(volume) == int(self.volume):
                    self.images.append(jpg)

    def _get_page_number(self, page):
        ''' Extract the page number from a given page url.'''
        return int(re.split(r'[_.]', page)[-2])

    def _sort_images(self):
        ''' Sort all images by page number.'''
        sorted_volume = sorted(self.images,
                               key=self._get_page_number)
        fully_sorted_volume = [os.path.join(JPG_DIR, x) for x in sorted_volume]
        self.images = fully_sorted_volume

    def _set_filename(self):
        ''' Set filename for converted pdf/cbz file.'''
        basename = f'{self.manga}_volume_{self.volume}.{self.type}'
        self.filename = os.path.join(MANGA_DIR, self.manga, basename)

    def _create_manga_dir(self):
        ''' Create a manga directory if it does not exist.'''
        manga_dir = os.path.join(MANGA_DIR, self.manga)
        if not os.path.exists(manga_dir):
            os.makedirs(manga_dir)

    def _convert_to_pdf(self):
        ''' Convert all images to a PDF file.'''
        cover = Image.open(self.images[0])
        width, height = cover.size
        pdf = FPDF(unit='pt', format=[width, height])
        for page in self.images:
            pdf.add_page()
            pdf.image(str(page), 0, 0)
        pdf.output(self.filename, 'F')

    def _convert_to_cbz(self):
        ''' Convert all images to a CBZ file.'''
        with zipfile.ZipFile(self.filename, 'w') as cbz:
            for page in self.images:
                cbz.write(page, page)

    def _get_conversion_method(self):
        ''' Returns the appropriate image conversion method.'''
        conversion_method = {'pdf': self._convert_to_pdf,
                             'cbz': self._convert_to_cbz}
        return conversion_method.get(self.type)

    def convert_volume(self, volume):
        ''' Convert images of a specific volume number to a pdf/cbz file.'''
        self.volume = volume
        self._get_volume_images()
        self._sort_images()
        self._set_filename()
        self._create_manga_dir()
        converter = self._get_conversion_method()
        converter()
        logging.info(f'Created {self.filename}')

    def convert_all_volumes(self):
        ''' Convert all images to their respective volume pdf/cbz files.'''
        volumes = set(x.split("_")[1] for x in os.listdir(JPG_DIR)
                      if self.manga in x)
        for volume in sorted(volumes):
            self.convert_volume(volume)
            self.images = []
