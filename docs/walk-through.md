# Walk Through

Allow one to search and download Mangas from from some providers (site parser) and to optionally upload them to a cloud storage service (DropBox, MegaUpload etc.)


Uses argparse to parse the search term to the search menu:
- given a specific site parser, we:
  - search and scrape the contents using bs4
  - return the results in a consistent format so they can be consumed by the menu
- it constructs an ASCII like menu to select the manga and volume(s) of interest
- upon selection we parse the results back to the parser with the manga and volume
- parser then downloads the volumes locally using a processing pool
- upload all files downloaded to a given file hosting site


The interface for each manga site class (site parsers) and uploaders use the adapter pattern, this allows one to easily add a new site by ensuring the same interface is used across all.

# Scaling
