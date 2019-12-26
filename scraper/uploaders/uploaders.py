import logging
from pathlib import Path
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

    def volume_exists(self, volume: Volume) -> bool:
        try:
            volume_search = self.api.files_search(
                path=str(volume.upload_path.parent), query=str(volume.upload_path.name),
            )
            return True if volume_search.matches else False
        except dropbox.exceptions.ApiError as e:
            actual_error = str(e.error._value)
            if "not_found" in actual_error:
                return False
            raise e

    def upload_volume(self, volume: Volume) -> None:
        if self.volume_exists(volume):
            self.adapter.warning(
                f"Volume {volume.upload_path} already exists in Dropbox"
            )
            return None
        with open(volume.file_path, "rb") as cbz:
            response = self.api.files_upload(cbz.read(), str(volume.upload_path))
            self.adapter.info(f"Uploaded to {response.path_lower}")


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
        Creates directory in pCloud
        """
        res = self.api.listfolder(path=dirname)
        if res.get("error"):
            if res["result"] == 2005:
                self.adapter.info(f"creatind directory {dirname}")
                response = self.api.createfolder(path=dirname)
                return response
        return {}

    def create_directories_recursively(self, filename: Path) -> None:
        """
        Splits a path up and creates each subdirectory down the path tree
        """
        for i in reversed(range(1, len(filename.parts) - 1)):
            directory = filename.parents[i - 1]
            res = self.create_directory(str(directory))
            if res.get("error"):
                raise IOError(res.get("error"))

    def upload_volume(self, volume: Volume) -> None:
        self.create_directories_recursively(volume.upload_path)
        parent_dir = str(volume.upload_path.parent)
        response = self.api.uploadfile(
            data=volume.file_path.read_bytes(),
            filename=str(volume.upload_path),
            path=parent_dir,
        )
        if response.get("error"):
            raise IOError(response.get("error"))
        self.adapter.info(f"Uploaded to {volume.upload_path}")
