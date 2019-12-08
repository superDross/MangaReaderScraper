"""
Pytest fixtures
"""

from unittest import mock

import pytest

from scraper.manga import Manga, MangaBuilder, Page, Volume


@pytest.fixture(scope="session", autouse=True)
def mocked_manga_env_var():
    """
    Mock MANGA_DIR env var in manga module to point to test jpg dir
    """
    mock_dir = f"/tmp"
    with mock.patch("scraper.manga.MANGA_DIR", mock_dir) as mocked_dir:
        yield mocked_dir


@pytest.fixture
def volume():
    page_data = [(1, b"here"), (2, b"bye")]
    volume = Volume(1, "/Some/path")
    volume.pages = page_data
    return volume


@pytest.fixture
def manga():
    manga = Manga("dragon-ball", "pdf")
    manga.volumes = [1, 2]
    manga.volume[1].pages = [(1, b"here"), (2, b"bye")]
    manga.volume[2].pages = [(1, b"hello"), (2, b"jimmy")]
    return manga
