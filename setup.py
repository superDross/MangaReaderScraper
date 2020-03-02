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

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

with open("requirements.txt", "r") as req:
    requirments = req.read().strip().split("\n")

setuptools.setup(
    name="MangaReaderScraper",
    # should correlate with git tag
    version=version,
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
    install_requires=requirments,
)
