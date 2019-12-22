import logging

from typing import Any, Dict

import dropbox
from mega import Mega
from pcloud import PyCloud

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
                self.adapter.info(f"Uploaded to {response.path_lower}")
            except dropbox.exceptions.ApiError as e:
                actual_error = e.error._value
                if actual_error.reason.is_conflict:
                    self.adapter.warning(
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
            self.adapter.info(f"Creating directory {dirname}")
            response = self.api.create_folder(dirname)
            self.dirname = list(response.values())[0]
        else:
            self.dirname = dir_metadata[0]

    def upload_volume(self, volume: Volume) -> None:
        if self.api.find(volume.file_path.name):
            self.adapter.warning(f"volume {volume.upload_path} already exists in Mega")
            return None
        self.api.upload(
            filename=volume.file_path,
            dest=self.dirname,
            dest_filename=volume.file_path.name,
        )
        self.adapter.info(f"Uploaded to {volume.upload_path}")

    def upload(self, manga: Manga) -> None:
        self._set_dirname(manga)
        super().upload(manga)


class PcloudUploader(BaseUploader):
    """
    Uploads manga volumes to pCloud
    """

    def __init__(self) -> None:
        super().__init__(service="pcloud")

    def _get_api_object(self) -> PyCloud:
        return PyCloud(self.config["email"], self.config["password"])

    def create_directory(self, dirname: str) -> Dict[str, Any]:
        """
        Creates directory in pCloud to save file to
        """
        res = self.api.listfolder(path=dirname)
        if res.get("error"):
            if res["result"] == 2005:
                self.adapter.info(f"creatind directory {dirname}")
                response = self.api.createfolder(path=dirname)
                return response
        return {}

    def upload_volume(self, volume: Volume) -> None:
        parent_dir = str(volume.upload_path.parent)
        res = self.create_directory(parent_dir)
        if res.get("error"):
            raise IOError(res.get("error"))
        response = self.api.uploadfile(
            data=volume.file_path.read_bytes(),
            filename=str(volume.upload_path),
            path=parent_dir,
        )
        if response.get("error"):
            raise IOError(response.get("error"))
        self.adapter.info(f"Uploaded to {volume.upload_path}")
