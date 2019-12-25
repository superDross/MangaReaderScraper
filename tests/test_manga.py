from pathlib import Path

import pytest

from scraper.exceptions import PageAlreadyPresent, VolumeAlreadyPresent
from scraper.manga import Manga, MangaBuilder, Page, Volume
from tests.helpers import MockedSiteParser


def test_page_repr(page):
    expected = f"Page(number={page.number}, img=True)"
    assert page.__repr__() == expected


def test_page_str(page):
    expected = f"Page(number={page.number}, img=True)"
    assert page.__str__() == expected


def test_volume_add_page():
    volume = Volume(1, "/Some/path", "/some/path")
    volume.add_page(1, b"bytes")
    assert volume.page == {1: Page(number=1, img=b"bytes")}
    assert volume.page[1] == Page(number=1, img=b"bytes")


def test_add_multiple_pages_to_volume():
    page_data = [(1, b"here"), (2, b"bye")]
    volume = Volume(1, "/Some/path", "/some/path")
    volume.pages = page_data
    assert volume.page[1] == Page(number=1, img=b"here")
    assert volume.page[2] == Page(number=2, img=b"bye")
    assert len(volume.page) == 2


def test_volume_repr(volume):
    expected = f"Volume(number={volume.number}, pages={len(volume.pages)})"
    assert volume.__repr__() == expected


def test_volume_str(volume):
    expected = f"Volume(number={volume.number}, pages={len(volume.pages)})"
    assert volume.__str__() == expected


def test_volume_iter(volume):
    generator = volume.__iter__()
    values = list(generator)
    assert values == volume.pages


def test_volume_total_pages(volume):
    assert volume.total_pages() == 2


def test_cant_add_page_already_in_volume(volume):
    with pytest.raises(PageAlreadyPresent):
        volume.add_page(1, b"something")


def test_pages_property_in_volume_returns_a_sorted_list(volume):
    volume.add_page(12, b"blah")
    volume.add_page(6, b"jk")
    volume.add_page(3, b"something")
    img1 = open("tests/test_files/jpgs/test-manga_1_1.jpg", "rb")
    img2 = open("tests/test_files/jpgs/test-manga_1_2.jpg", "rb")
    expected = [
        Page(1, img1.read()),
        Page(2, img2.read()),
        Page(3, b"something"),
        Page(6, b"jk"),
        Page(12, b"blah"),
    ]
    assert volume.pages == expected


def test_manga_get_volume_path():
    manga = Manga("dragon-ball", "pdf")
    volume_path = manga._volume_path(1)
    expected = "/tmp/dragon-ball/dragon-ball_volume_1.pdf"
    assert str(volume_path) == expected


def test_manga_get_volume_path_cbz():
    manga = Manga("dragon-ball", "cbz")
    volume_path = manga._volume_path(1)
    expected = "/tmp/dragon-ball/dragon-ball_volume_1.cbz"
    assert str(volume_path) == expected


def test_manga_add_volume():
    manga = Manga("dragon-ball", "pdf")
    manga.add_volume(1)
    v1 = Volume(
        number=1,
        file_path="/tmp/dragon-ball/dragon-ball_volume_1.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_1.pdf"),
    )
    assert manga.volume == {1: v1}
    assert manga.volume[1] == v1


def test_add_multiple_volumes_to_manga():
    manga = Manga("dragon-ball", "pdf")
    manga.volumes = [1, 2]
    assert manga.volume[1] == Volume(
        number=1,
        file_path="/tmp/dragon-ball/dragon-ball_volume_1.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_1.pdf"),
    )
    assert manga.volume[2] == Volume(
        number=2,
        file_path="/tmp/dragon-ball/dragon-ball_volume_2.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_2.pdf"),
    )
    assert len(manga.volume) == 2


def test_cant_add_volume_already_in_manga(manga):
    with pytest.raises(VolumeAlreadyPresent):
        manga.add_volume(1)


def test_volumes_property_in_manga_returns_a_sorted_list(manga):
    manga.add_volume(12)
    manga.add_volume(4)
    v1 = Volume(
        number=1,
        file_path="/tmp/dragon-ball/dragon-ball_volume_1.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_1.pdf"),
    )
    v2 = Volume(
        number=2,
        file_path="/tmp/dragon-ball/dragon-ball_volume_2.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_2.pdf"),
    )
    v3 = Volume(
        number=4,
        file_path="/tmp/dragon-ball/dragon-ball_volume_4.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_4.pdf"),
    )
    v4 = Volume(
        number=12,
        file_path="/tmp/dragon-ball/dragon-ball_volume_12.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_12.pdf"),
    )
    v1.pages = [(1, b"here"), (2, b"bye")]
    v2.pages = [(1, b"hello"), (2, b"jimmy")]
    expected = [
        v1,
        v2,
        v3,
        v4,
    ]
    assert manga.volumes == expected


def test_get_page_2_from_manga(manga):
    assert manga.volume[1].page[2] == Page(2, b"bye")


def test_manga_repr(manga):
    expected = f"Manga(name={manga.name}, volumes={len(manga.volumes)})"
    assert manga.__repr__() == expected


def test_manga_str(manga):
    expected = f"Manga(name={manga.name}, volumes={len(manga.volumes)})"
    assert manga.__str__() == expected


def test_manga_iter(manga):
    generator = manga.__iter__()
    values = list(generator)
    assert values == manga.volumes


@pytest.mark.parametrize("inval", [[1, 2, 3], None])
def test_mangabuilder_get_all_volumes(inval):
    parser = MockedSiteParser()
    builder = MangaBuilder(parser)
    manga = builder.get_manga_volumes(vol_nums=inval)
    v1 = Volume(
        number=1,
        file_path="/tmp/dragon-ball/dragon-ball_volume_1.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_1.pdf"),
    )
    v2 = Volume(
        number=2,
        file_path="/tmp/dragon-ball/dragon-ball_volume_2.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_2.pdf"),
    )
    v3 = Volume(
        number=3,
        file_path="/tmp/dragon-ball/dragon-ball_volume_3.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_3.pdf"),
    )
    img1 = open("tests/test_files/jpgs/test-manga_1_1.jpg", "rb")
    img2 = open("tests/test_files/jpgs/test-manga_1_2.jpg", "rb")
    pages = [(1, img1.read()), (2, img2.read())]
    v1.pages = pages
    v2.pages = pages
    v3.pages = pages
    assert manga.volume[2].upload_path == v2.upload_path
    assert manga.volume[1].page[1] == v1.page[1]
    assert manga.volume[3].page[2] == v1.page[2]
    assert manga.volumes == [v1, v2, v3]


def test_mangabuilder_get_single_volumes(parser):
    parser = MockedSiteParser()
    builder = MangaBuilder(parser)
    manga = builder.get_manga_volumes(vol_nums=[1])
    v1 = Volume(
        number=1,
        file_path="/tmp/dragon-ball/dragon-ball_volume_1.pdf",
        upload_path=Path("/dragon-ball/dragon-ball_volume_1.pdf"),
    )
    img1 = open("tests/test_files/jpgs/test-manga_1_1.jpg", "rb")
    img2 = open("tests/test_files/jpgs/test-manga_1_2.jpg", "rb")
    pages = [(1, img1.read()), (2, img2.read())]
    v1.pages = pages
    assert manga.volumes == [v1]
    assert manga.volume[1] == v1
    assert manga.volume[1].page[1] == v1.page[1]


def test_manga_builder_preferred_name(parser):
    parser = MockedSiteParser()
    builder = MangaBuilder(parser)
    manga = builder.get_manga_volumes(vol_nums=[1], preferred_name="smelly_pancakes")
    v1 = Volume(
        number=1,
        file_path="/tmp/smelly_pancakes/smelly_pancakes_volume_1.pdf",
        upload_path=Path("/smelly_pancakes/smelly_pancakes_volume_1.pdf"),
    )
    img1 = open("tests/test_files/jpgs/test-manga_1_1.jpg", "rb")
    img2 = open("tests/test_files/jpgs/test-manga_1_2.jpg", "rb")
    pages = [(1, img1.read()), (2, img2.read())]
    v1.pages = pages
    assert manga.volume[1] == v1
