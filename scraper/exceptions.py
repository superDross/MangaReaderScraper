"""
Custom exceptions
"""


class VolumeDoesntExist(Exception):
    pass


class MangaDoesNotExist(Exception):
    pass


class PageAlreadyPresent(Exception):
    pass


class VolumeAlreadyPresent(Exception):
    pass


class VolumeAlreadyExists(Exception):
    pass


class InvalidOption(Exception):
    pass


class MangaParserNotSet(Exception):
    pass


class CannotExtractChapter(Exception):
    pass
