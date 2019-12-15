import os
import shutil
from pathlib import Path
from unittest import mock

import pytest

from scraper.download import Download, download_manga


@pytest.mark.parametrize("filetype,file_signature", [("pdf", "%PDF-"), ("cbz", "PK")])
def test_download_manga(filetype, file_signature, parser):
    with mock.patch("scraper.manga.MangaParser", parser):
        downloader = Download("dragon-ball", filetype)
        downloader.download_volumes([1])
        expected_path = f"/tmp/dragon-ball/dragon-ball_volume_1.{filetype}"
        assert os.path.exists(expected_path)
        # check file for PDF/CBZ signature
        with open(expected_path, "rb") as pdf_file:
            pdf = pdf_file.read().decode("utf-8", "ignore")
            assert pdf.startswith(file_signature)


def test_download_manga_helper_function(parser):
    with mock.patch("scraper.manga.MangaParser", parser):
        download_manga("dragon-ball", [1, 2], "pdf")
        expected_path = "/tmp/dragon-ball/dragon-ball_volume_1.pdf"
        expected_path2 = "/tmp/dragon-ball/dragon-ball_volume_2.pdf"
        assert os.path.exists(expected_path)
        assert os.path.exists(expected_path2)


def teardown_module(module):
    """
    Remove directories after every test, if present

    Fixtures only work before a test is executed, hence
    the need for this module teardown.
    """
    tmp_dir = Path("/tmp/dragon-ball")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
