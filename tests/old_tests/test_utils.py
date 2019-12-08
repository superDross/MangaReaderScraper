from scraper.utils import CustomAdapter, get_adapter


def test_case_adapter(caplog, logger):
    adapter = CustomAdapter(
        logger, extra={"manga": "dragon-ball-super-gt-z-heroes", "volume": 1}
    )
    adapter.warning("Test message")
    assert "[Dragon Ball Super Gt Z Heroes:1] Test message" in caplog.text


def test_case_adapter_manga_only(caplog, logger):
    adapter = CustomAdapter(logger, extra={"manga": "dragon-ball-super-gt-z-heroes"})
    adapter.warning("Test message")
    assert "[Dragon Ball Super Gt Z Heroes] Test message" in caplog.text


def test_get_adapter(caplog, logger):
    adapter = get_adapter(logger, manga="cool-manga", volume=2)
    adapter.warning("Test message")
    assert "[Cool Manga:2] Test message" in caplog.text
