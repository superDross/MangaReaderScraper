"""
Custom type hints
"""

from typing import Tuple, TypeVar

PageData = TypeVar("PageData", bound=Tuple[int, bytes])
VolumeData = TypeVar("VolumeData", bound=Tuple[int, PageData])
