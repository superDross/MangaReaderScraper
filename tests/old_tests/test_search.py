import bs4

from scraper.search import Search


def test_get_search_results():
    search = Search()
    results = search._get_search_results("dragonball")
    assert isinstance(results, bs4.element.ResultSet)
    assert len(results) == 6


def test_extract_text():
    search = Search()
    results = search._get_search_results("dragonball")
    search_dict = search._extract_text(results[0])
    expected = {
        "title": "Dragon Ball",
        "manga_url": "dragon-ball",
        "chapters": "520",
        "type": "Manga ",
    }
    assert expected == search_dict


def test_extract_metadata():
    search = Search()
    results = search._get_search_results("dragonball")
    search._extract_metadata(results)
    expected = {
        "1": {
            "title": "Dragon Ball",
            "manga_url": "dragon-ball",
            "chapters": "520",
            "type": "Manga ",
        },
        "2": {
            "title": "Dragon Ball SD",
            "manga_url": "dragon-ball-sd",
            "chapters": "34",
            "type": "Manga ",
        },
        "3": {
            "title": "Dragon Ball: Episode of Bardock",
            "manga_url": "dragon-ball-episode-of-bardock",
            "chapters": "3",
            "type": "Manga ",
        },
        "4": {
            "title": "DragonBall Next Gen",
            "manga_url": "dragonball-next-gen",
            "chapters": "4",
            "type": "Manga ",
        },
        "5": {
            "title": "Dragon Ball Z - Rebirth of F",
            "manga_url": "dragon-ball-z-rebirth-of-f",
            "chapters": "3",
            "type": "Manga ",
        },
        "6": {
            "title": "Dragon Ball Super",
            "manga_url": "dragon-ball-super",
            "chapters": "54",
            "type": "Manga ",
        },
    }
    assert search.results == expected


def test_search_table_returned():
    search = Search()
    search.search("dragonball")
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
    assert search.table == expected
