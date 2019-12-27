from pathlib import Path
from unittest import mock

import pytest

from scraper.manga import Manga
from scraper.uploaders.uploaders import DropboxUploader, MegaUploader, PcloudUploader
from tests.helpers import (
    MockedDropbox,
    MockedDropboxRealFile,
    MockedMega,
    MockedMegaNotFound,
    MockedPyCloud,
    MockedPyCloudFail,
    setup_uploader,
)


@pytest.mark.parametrize("uploader", [DropboxUploader, MegaUploader])
@mock.patch("scraper.uploaders.uploaders.Mega", MockedMega)
@mock.patch("scraper.uploaders.uploaders.dropbox.Dropbox", MockedDropbox)
def test_upload_fails(caplog, volume, uploader):
    uploader = setup_uploader(uploader)
    response = uploader.upload_volume(volume)
    assert "already exists" in caplog.text
    assert response is None


@mock.patch("scraper.uploaders.uploaders.dropbox.Dropbox", MockedDropboxRealFile)
def test_dropbox_upload(caplog, volume):
    volume.file_path = "tests/test_files/mangakaka/dragonball_super_page.html"
    dbox = setup_uploader(DropboxUploader)
    response = dbox.upload_volume(volume)
    assert response.text == "success"


@mock.patch("scraper.uploaders.uploaders.Mega", MockedMegaNotFound)
def test_mega_upload(volume):
    mega = setup_uploader(MegaUploader)
    response = mega.upload_volume(volume)
    assert response == {"status": "success"}


@mock.patch("scraper.uploaders.uploaders.Mega", MockedMega)
def test_mega_set_dirname():
    manga = Manga("dragon-ball", "pdf")
    manga.add_volume(1)
    mega = setup_uploader(MegaUploader)
    mega.set_dirname(manga)
    assert mega.dirname == "start"


@mock.patch("scraper.uploaders.uploaders.Mega", MockedMegaNotFound)
def test_mega_set_dirname_if_dir_not_in_cloud():
    manga = Manga("dragon-ball", "pdf")
    manga.add_volume(1)
    mega = setup_uploader(MegaUploader)
    mega.set_dirname(manga)
    assert mega.dirname == "two"


@mock.patch("scraper.uploaders.uploaders.PyCloud", MockedPyCloud)
def test_pycloud_create_directory_if_not_present_in_the_cloud():
    pycloud = setup_uploader(PcloudUploader)
    response = pycloud.create_directory("/path")
    assert response == {"result": 0, "metadata": "path"}


def test_pycloud_create_directory_returns_nothing_if_dir_in_cloud():
    with mock.patch("scraper.uploaders.uploaders.PyCloud", MockedPyCloudFail) as mm:
        mm.listed = {}
        pycloud = setup_uploader(PcloudUploader)
        response = pycloud.create_directory("/path")
        assert response == {}


@mock.patch("scraper.uploaders.uploaders.PyCloud", MockedPyCloud)
def test_pycloud_create_directories():
    file = Path("/path/to/file.txt")
    pycloud = setup_uploader(PcloudUploader)
    responses = pycloud.create_directories_recursively(file)
    assert len(responses) == 2
    assert responses[0] == {"result": 0, "metadata": "path"}


@mock.patch("scraper.uploaders.uploaders.PyCloud", MockedPyCloudFail)
def test_pycloud_create_directories_fail():
    file = Path("/path/to/file.txt")
    with mock.patch("scraper.uploaders.uploaders.PyCloud", MockedPyCloudFail) as mm:
        mm.listed = {"error": True, "result": 2005}
        pycloud = setup_uploader(PcloudUploader)
        with pytest.raises(IOError):
            pycloud.create_directories_recursively(file)


@mock.patch("scraper.uploaders.uploaders.PyCloud", MockedPyCloud)
def test_pycloud_upload_volume(volume):
    volume.file_path = Path("tests/test_files/jpgs/test-manga_1_1.jpg")
    pycloud = setup_uploader(PcloudUploader)
    response = pycloud.upload_volume(volume)
    assert response == {"status": "success"}


@mock.patch("scraper.uploaders.uploaders.PyCloud", MockedPyCloudFail)
def test_pycloud_upload_upload_failure(volume):
    volume.file_path = Path("tests/test_files/jpgs/test-manga_1_1.jpg")
    pycloud = setup_uploader(PcloudUploader)
    with pytest.raises(IOError):
        pycloud.upload_volume(volume)


@pytest.mark.parametrize(
    "to_mock,mock_obj,uploader",
    [
        ("PyCloud", MockedPyCloud, PcloudUploader),
        ("Mega", MockedMegaNotFound, MegaUploader),
    ],
)
def test_upload_calls(to_mock, mock_obj, uploader):
    with mock.patch(f"scraper.uploaders.uploaders.{to_mock}", mock_obj):
        manga = Manga("dragon-ball", "pdf")
        manga.add_volume(1)
        manga.add_volume(2)
        manga.volume[1].file_path = Path("tests/test_files/jpgs/test-manga_1_1.jpg")
        manga.volume[2].file_path = Path("tests/test_files/jpgs/test-manga_1_2.jpg")
        uploader = setup_uploader(uploader)
        responses = uploader(manga)
        assert len(responses) == 2
        assert all(x == {"status": "success"} for x in responses)
