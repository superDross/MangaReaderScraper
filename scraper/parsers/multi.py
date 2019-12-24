class MultiParser:
    def __init__(self, manga_name: str, parsers: list) -> None:
        self.parsers = parsers
        self.manga_name = manga_name
