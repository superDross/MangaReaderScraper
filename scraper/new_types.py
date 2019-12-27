"""
Custom type hints & aliases
"""

from typing import Dict, Iterable, Optional, Tuple

PageData = Tuple[int, bytes]
VolumeData = Tuple[int, Optional[Iterable[PageData]]]
SearchResults = Dict[str, Dict[str, str]]
