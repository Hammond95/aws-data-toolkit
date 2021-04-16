import os
import sys
import ntpath
from pathlib import Path
from typing import Union


def path_leaf(path: Union[str, Path]) -> str:
    """Returns the last part of any path."""

    # TODO: This may give wrong results for escaped paths
    # under linux/macos os. Should add a check of blackslashes
    # in the path if running on these platforms.

    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def human_readable_size(num, suffix="B"):
    """Given a size in bytes, returns an human readable
    representation of the size."""
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, "Yi", suffix)
