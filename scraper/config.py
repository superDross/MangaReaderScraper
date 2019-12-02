""" Stores global variables used across multiple modules."""
import os

HERE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
JPG_DIR = os.path.join(HERE, "jpgs")
MANGA_DIR = os.path.join(HERE, "mangas")
MANGA_URL = "http://mangareader.net"
