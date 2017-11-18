''' Custom exceptions used througout the package.'''


class MangaDoesntExist(Exception):
    ''' Raise if the manga doesn't exist in MangaReader.'''
    def __init__(self, manga, msg=None):
        if not msg:
            msg = '{} is not available at mangareader.net'.format(manga)
        Exception.__init__(self, msg)
        self.manga = manga
        self.msg = msg


class VolumeDoesntExist(Exception):
    ''' Raise if the volume doesn't exist in MangaReader.'''
    def __init__(self, manga, volume, msg=None):
        if not msg:
            msg = '{} volume {} is not available at mangareader.net'.format(
                    manga, volume)
        Exception.__init__(self, msg)
        self.manga = manga
        self.volume = volume
        self.msg = msg
