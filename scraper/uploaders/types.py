from typing import Union

from scraper.uploaders.uploaders import DropboxUploader, MegaUploader, PcloudUploader

Uploader = Union[DropboxUploader, MegaUploader, PcloudUploader]
