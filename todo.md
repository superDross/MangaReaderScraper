# TODO

## Refactor

### Essential

- Create a Producer (name pending) that composes Download and Converter via composition.
  - Download methods MUST return Volume object(s) which can be passed to Converter
  - Page now have `file_path` so Converters complexity can be reduced.
- Use config file to determine where to download mangas to (package default config file too)
- delete jpgs after converting to pdf/cbz

### Optional

- Manga class

  - holds all Volume objects in a dict {volumenumber: Volume} `self._volumes`
  - `__iter__` convert volumes dict to sorted list and iterate
  - `add()` method `self._volumes[volume.number] = volume`
  - To get a volume `manga.volumes[2]`

- Volume Class
  - edit to contain pages via a dict, like Manga contains `self._volumes`
  - To get a page image `manga.volumes[4].pages[10].img`

## Future

- remove `config.py` and use a settings config file instead
- complete test coverage
- make changes to GUI (see `gui.py`)
- use pathlib instea of os module
- mypy for type checking

## Nice to Haves

- Travis CI
- Docker? Not sure if pointless as it is not a web app.
