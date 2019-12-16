"""
Custom type hints & aliases
"""

from typing import Iterable, Tuple

PageData = Tuple[int, bytes]
VolumeData = Tuple[int, Iterable[PageData]]
