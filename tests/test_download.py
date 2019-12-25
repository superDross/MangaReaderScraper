import os
import shutil
from pathlib import Path

import pytest

from scraper.__main__ import download_manga
from scraper.download import Download
from tests.helpers import MockedSiteParser


@pytest.mark.parametrize("filetype,file_signature", [("pdf", "%PDF-"), ("cbz", "PK")])
def test_download_manga(filetype, file_signature):
    downloader = Download("dragon-ball", filetype, MockedSiteParser)
    downloader.download_volumes([1])
    expected_path = f"/tmp/dragon-ball/dragon-ball_volume_1.{filetype}"
    assert os.path.exists(expected_path)
    # check file for PDF/CBZ signature
    with open(expected_path, "rb") as pdf_file:
        pdf = pdf_file.read().decode("utf-8", "ignore")
        assert pdf.startswith(file_signature)


def test_download_manga_helper_function(parser):
    download_manga(
        manga_name="dragon-ball",
        volumes=[1, 2],
        filetype="pdf",
        parser=MockedSiteParser,
        preferred_name="cool_mo_deep",
    )
    expected_path = "/tmp/cool_mo_deep/cool_mo_deep_volume_1.pdf"
    expected_path2 = "/tmp/cool_mo_deep/cool_mo_deep_volume_2.pdf"
    assert os.path.exists(expected_path)
    assert os.path.exists(expected_path2)


def test_download_manga_helper_function_preffered_name(parser):
    download_manga("dragon-ball", [1, 2], "pdf", MockedSiteParser)
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
