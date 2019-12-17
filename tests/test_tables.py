from unittest import mock

from scraper.parsers import MangaReaderSearch
from scraper.tables import TableProducer
from tests.helpers import METADATA


def test_generate():
    with mock.patch("scraper.tables.MangaReaderSearch.metadata") as mocked:
        mocked.return_value = METADATA

        searcher = MangaReaderSearch(["dragon", "ball"])
        producer = TableProducer()
        table = producer.generate(searcher)
        expected = (
            "+----+---------------------------------+-----------+--------+\n"
            "|    | Title                           |   Volumes | Type   |\n"
            "|----+---------------------------------+-----------+--------|\n"
            "|  1 | Dragon Ball                     |       520 | Manga  |\n"
            "|  2 | Dragon Ball SD                  |        34 | Manga  |\n"
            "|  3 | Dragon Ball: Episode of Bardock |         3 | Manga  |\n"
            "|  4 | DragonBall Next Gen             |         4 | Manga  |\n"
            "|  5 | Dragon Ball Z - Rebirth of F    |         3 | Manga  |\n"
            "|  6 | Dragon Ball Super               |        54 | Manga  |\n"
            "+----+---------------------------------+-----------+--------+"
        )
        assert table == expected
