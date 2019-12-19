# MangaReaderScraper

Search & download mangas from the command line.

## Install

To install:

```bash
pip install --user MangaReaderScraper
```

For development:

```bash
git clone https://github.com/superDross/MangaReaderScraper
pip install -r MangaReaderScraper/requirements.txt
export PYTHONPATH=$PYTHONPATH:/path/to/MangaReaderScraper/
```

## Options

`--search` Search mangareader.net for a given query and select to download one of the mangas from the parsed searched results. <br />
`--manga` Manga series name to download. <br />
`--volumes` Manga series volume number to download. <br />
`--cbz` Store in CBZ format instead of PDF. <br />
`--output` Directory to save downloads (defaults to `~/Downloads`) <br />
`--source` Website to scrape from <br />
`--upload` Upload mangas to a cloud storage service <br />

## Uploading

### Dropbox

Follow this [guide](https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/) to create a token. Then place the token into your config (`~/.config/mangarscraper.ini`):

```
[dropbox]
token = hdkd87799jjjj
```

### Mega

Add your email and password to the config file:

```
[mega]
email = email@email.com
password = notapassword123
```

## Example Usage

After using the search function, a table will appear and you will be asked to select a specific manga (type a number in the first column). You will subsequently be asked to download a specific volume. In the example below, Dragon Ball Super volume 1 has been selected for download.

```
$ manga-scraper --search dragon ball

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

>> 5

Dragon Ball Super has been selected for download.
Which volume do you want to download (Enter alone to download all volumes)?

>> 1-25 33 56
```

To download a manga directly:

```
# Download all Dragon Ball volumes & upload to dropbox
manga-scraper --manga dragon-ball --upload dropbox

# Download volume 2 of the Final Fantasy XII manga
manga-scraper --manga final-fantasy-xii --volumes 2

# Download Dragon Ball Super volumes 3-7 & 23
manga-scraper --manga dragon-ball-super --volumes 3-7 23
```
