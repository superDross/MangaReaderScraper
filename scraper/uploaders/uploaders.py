import logging

import dropbox
from mega import Mega

from scraper.manga import Manga, Volume
from scraper.uploaders.base import BaseUploader

logger = logging.getLogger(__name__)


class DropboxUploader(BaseUploader):
    """
    Uploads manga volumes to Dropbox
    """

    def __init__(self) -> None:
        super().__init__(service="dropbox")

    def _get_api_object(self) -> dropbox.Dropbox:
        return dropbox.Dropbox(self.config["token"])

    def upload_volume(self, volume: Volume) -> None:
        with open(volume.file_path, "rb") as cbz:
            try:
                response = self.api.files_upload(cbz.read(), str(volume.upload_path))
                logger.info(f"Uploaded to {response.path_lower}")
            except dropbox.exceptions.ApiError as e:
                actual_error = e.error._value
                if actual_error.reason.is_conflict:
                    logger.warning(
                        f"Volume {volume.upload_path} already exists in Dropbox"
                    )
                    return None
                raise e


class MegaUploader(BaseUploader):
    """
    Uploads manga volumes to Mega
    """

    def __init__(self) -> None:
        super().__init__(service="mega")
        self.dirname: str = None

    def _get_api_object(self) -> Mega:
        mega = Mega()
        return mega.login(self.config["email"], self.config["password"])

    def _set_dirname(self, manga: Manga) -> None:
        """
        Sets the directory key. The name you give a directory is not
        how Mega store it, its a bunch of random letters instead.
        """
        dirname = f"/{manga.name}/"
        dir_metadata = self.api.find(dirname)
        if not dir_metadata:
            logger.info(f"Creating directory {dirname}")
            response = self.api.create_folder(dirname)
            self.dirname = list(response.values())[0]
        else:
            self.dirname = dir_metadata[0]

    def upload_volume(self, volume: Volume) -> None:
        if self.api.find(volume.file_path.name):
            logger.warning(f"volume {volume.upload_path} already exists in Mega")
            return None
        self.api.upload(
            filename=volume.file_path,
            dest=self.dirname,
            dest_filename=volume.file_path.name,
        )
        logger.info(f"Uploaded to {volume.upload_path}")

    def upload(self, manga: Manga) -> None:
        self._set_dirname(manga)
        super().upload(manga)
