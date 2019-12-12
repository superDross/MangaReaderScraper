from typing import Optional


class VolumeDoesntExist(Exception):
    """
    Raise if the volume doesn't exist in MangaReader
    """

    def __init__(self, manga: str, volume: str, msg: Optional[str] = None) -> None:
        if not msg:
            msg = f"{manga} volume {volume} is not available at mangareader.net"
        Exception.__init__(self, msg)
        self.manga = manga
        self.volume = volume
        self.msg = msg


class MangaDoesNotExist(Exception):
    def __init__(self, manga: str, msg: Optional[str] = None) -> None:
        if not msg:
            msg = f"Manga {manga} does not exist"
        Exception.__init__(self, msg)
        self.manga = manga
        self.msg = msg


class PageAlreadyPresent(Exception):
    pass


class VolumeAlreadyPresent(Exception):
    pass


class InvalidOption(Exception):
    pass
