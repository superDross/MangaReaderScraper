# MangaReaderScraper

Search and download specific volumes of a manga series from MangaReader and store as a PDF.

## Install

To install:

```bash
git clone https://github.com/superDross/MangaReaderScraper
pip3 install -r MangaReaderScraper/requirements.txt
export PYTHONPATH=$PYTHONPATH:/path/to/MangaReaderScraper/
```

## GUI

To use the GUI instead of the CLI, simply don't parse any args:

```bash
python3 MangaReaderScraper
```

## CLI

### Options

`--search` Search mangareader.net for a given query and select to download one of the mangas from the parsed searched results. <br />
`--manga` Manga series name to download. <br />
`--volume` Manga series volume number to download. <br />
`--cbz` Store in CBZ format instead of PDF. <br />

### Example Usage

After using the search function, a table will appear and you will be asked to select a specific manga (type a number in the first column). You will subsequently be asked to download a specific volume. In the example below, Dragon Ball Super volume 1 has been selected for download.

```
$ python3 MangaReaderScraper --search dragon ball

+----+---------------------------------+-----------+--------+
|    | Title                           |   Volumes | Type   |
|----+---------------------------------+-----------+--------|
|  0 | Dragon Ball: Episode of Bardock |         3 | Manga  |
|  1 | Dragon Ball SD                  |        20 | Manga  |
|  2 | DragonBall Next Gen             |         4 | Manga  |
|  3 | Dragon Ball                     |       520 | Manga  |
|  4 | Dragon Ball Z - Rebirth of F    |         3 | Manga  |
|  5 | Dragon Ball Super               |        29 | Manga  |
+----+---------------------------------+-----------+--------+
Select manga number
5
Dragon Ball Super has been selected for download.
Which volume do you want to download (Enter alone to download all volumes)?
1
```

To simply download a manga series volumes:

```
# Download all Dragon Ball volumes
python3 MangaReaderScraper --manga dragon-ball

# Download volume 2 of the Final Fantasy XII manga
python3 MangaReaderScraper --manga final-fantasy-xii --volume 2
```
