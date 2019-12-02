from unittest import mock

import pytest

from scraper.config import HERE
from scraper.converter import Conversion


@pytest.mark.parametrize("inval, output", [("pdf", "pdf"), ("cbz", "cbz")])
def test_type_setting(inval, output):
    converter = Conversion("something")
    converter.type = inval
    assert converter.type == output


def test_wrong_type_setting():
    with pytest.raises(ValueError):
        converter = Conversion("something")
        converter.type = "csv"


def test_get_volume_images(converter):
    converter._get_volume_images()
    expected = ["test-manga_1_1.jpg", "test-manga_1_2.jpg", "test-manga_1_3.jpg"]
    assert converter.images == expected


def test_extract_page_number(converter, test_jpg_dir):
    test_jpg = f"{test_jpg_dir}/test-manga_1_3.jpg"
    page_number = converter._get_page_number(test_jpg)
    assert page_number == 3


def test_sort_images(converter):
    converter._get_volume_images()
    converter._sort_images()
    expected = [
        f"{HERE}/tests/test_files/jpgs/test-manga_1_1.jpg",
        f"{HERE}/tests/test_files/jpgs/test-manga_1_2.jpg",
        f"{HERE}/tests/test_files/jpgs/test-manga_1_3.jpg",
    ]
    assert expected == converter.images


def test_set_filename(converter):
    converter.type = "pdf"
    converter._set_filename()
    expected = f"{HERE}/tests/test_files/jpgs/test-manga/test-manga_volume_1.pdf"
    assert expected == converter.filename


# def test_convert_to_cbz(converter):
#     converter.type = "cbz"
#     converter._get_volume_images()
#     converter._sort_images()
#     converter._convert_to_cbz()
