import abc
import logging
from multiprocessing.pool import ThreadPool
from typing import Any

import dropbox
from mega import Mega

from scraper.manga import Manga, Volume
from scraper.utils import settings

logger = logging.getLogger(__name__)


class BaseUploader:
    """
    Base class for uploading to cloud storage services
    """

    def __init__(self, service: str) -> None:
        self.service = service
        self.config = settings()[service]
        self.api = self._get_api_object()

    def __call__(self, manga: Manga):
        return self.upload(manga)

    @abc.abstractmethod
    def _get_api_object(self) -> Any:
        """
        Returns an object used for uploading data to the service
        """
        pass

    @abc.abstractmethod
    def upload_volume(self, volume: Volume) -> None:
        """
        Uploads a given volume
        """
        pass

    def upload(self, manga: Manga) -> None:
        """
        Uploads all volumes in a given Manga object
        """
        logger.info(f"Uploading to {self.service.title()}")
        with ThreadPool() as pool:
            pool.map(self.upload_volume, manga.volumes)


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

    def _set_dirname(self, manga: Manga):
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

    def upload_volume(self, volume: Volume):
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


def upload(manga, service):
    services = {"dropbox": DropboxUploader, "mega": MegaUploader}
    uploader = services[service]()
    return uploader(manga)
