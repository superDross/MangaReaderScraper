from scraper.tables import TableProducer


def test_generate(search_html):
    search_results = search_html.find_all("div", {"class": "mangaresultitem"})
    producer = TableProducer()
    table = producer.generate(search_results)
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
