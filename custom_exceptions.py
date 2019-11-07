""" Custom exceptions used througout the package."""


class VolumeDoesntExist(Exception):
    """ Raise if the volume doesn't exist in MangaReader."""

    def __init__(self, manga: str, volume: str, msg: str = None) -> None:
        if not msg:
            msg = f"{manga} volume {volume} is not available at mangareader.net"
        Exception.__init__(self, msg)
        self.manga = manga
        self.volume = volume
        self.msg = msg
