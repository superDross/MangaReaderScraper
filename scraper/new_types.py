"""
Custom type hints & aliases
"""

from typing import Dict, Iterable, Tuple

PageData = Tuple[int, bytes]
VolumeData = Tuple[int, Iterable[PageData]]
SearchResults = Dict[str, Dict[str, str]]
