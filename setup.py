"""
To install locally:
    python setup.py install

To upload to PyPi:
    python setup.py sdist
    pip install twine
    twine upload dist/*
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MangaReaderScraper",
    # should correlate with git tag
    version="0.4",
    author="superDross",
    author_email="dross78375@gmail.com",
    description="Manga scraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/superDross/MangaReaderScraper",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points={"console_scripts": ["manga-scraper = scraper.__main__:cli_entry"]},
    install_requires=[
        "beautifulsoup4==4.8.1",
        "lxml==4.2.5",
        "Pillow==6.2.1",
        "reportlab==3.5.23",
        "requests==2.22.0",
        "tabulate==0.8.1",
        "dropbox==9.4.0",
        "mega.py==1.0.5",
        "pcloud==1.0a6",
    ],
)
