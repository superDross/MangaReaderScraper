from typing import Union
from scraper.uploaders.uploaders import DropboxUploader, MegaUploader

Uploader = Union[DropboxUploader, MegaUploader]
