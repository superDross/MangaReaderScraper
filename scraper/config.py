""" Stores global variables used across multiple modules."""
import os

# TODO: place this in a utils function
HERE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# TODO: put all the below vars in a settings.cfg file
MANGA_DIR = os.path.join(HERE, "mangas")
