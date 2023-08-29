import os
import logging
from typing import List

import fnmatch
import mkdocs

from .types import EzLinksOptions


class FileMapper:
    def __init__(
            self,
            options: EzLinksOptions,
            root: str,
            files: List[mkdocs.structure.pages.Page],
            logger=None):
        self.options = options
        self.root = root
        self.logger = logger

        # Drop any files outside of the root of the docs dir
        self.files = [file for file in files if root in file.abs_src_path]

    def search(self, from_file: str, file_path: str):
        abs_to = file_path
        # Detect if it's an absolute link, then just return it directly
        if abs_to.startswith('/'):
            return os.path.join(self.root, abs_to[1:])

        (fp, ext) = os.path.splitext(file_path)
        fp += ext if ext else ".*"
        hits = _find_closest_target(self.files, from_file, fp)

        if not hits:
            return abs_to

        if len(hits) > 1:
            log_fn = self.logger.warning if self.options.warn_ambiguities else self.logger.debug
            log_fn(f"[EzLink] Link ambiguity detected.\n"
                   f"File: '{from_file}'\n"
                   f"Link: '{file_path}'\n"
                   "Ambiguities:\n" + "\n\t".join(hits))

        ret = os.path.join(self.root, hits[0])
        print(f"---* {ret}")
        return ret


def _find_closest_target(file_list, path, pattern):
    pt = os.path.dirname(path).split("/")
    for ii in range(len(pt), -1, -1):
        _pt = pt[0:ii]
        xpt = os.path.join(*_pt) if _pt else ""
        xpt = os.path.join(xpt, "*", pattern)
        ret = _glob_list(file_list, xpt)
        if ret:
            return ret
    return _glob_list(file_list, pattern)


def _glob_list(file_list, pattern):
    matched_files = []
    for file_path in file_list:
        if fnmatch.fnmatch(file_path.src_uri, pattern):
            matched_files.append(file_path.src_uri)
    return matched_files
