"""Reads Lightroom-exported metadata (EXIF/IPTC/XMP) via exiftool.

exiftool must be on PATH (or pointed to via the EXIFTOOL_PATH env var).
If it's missing, or a file has no embedded metadata, extraction degrades
gracefully to an empty result rather than failing the upload.
"""

import json
import os
import subprocess
from datetime import datetime

EXIFTOOL_BIN = os.environ.get("EXIFTOOL_PATH", "exiftool")

TAGS = [
    "-DateTimeOriginal",
    "-Model",
    "-LensModel",
    "-Title",
    "-Caption-Abstract",
    "-Description",
    "-Keywords",
    "-HierarchicalSubject",
]

EMPTY_METADATA = {
    "title": None,
    "description": None,
    "date_taken": None,
    "camera": None,
    "lens": None,
    "keywords": [],
    "hierarchical_keywords": [],
}


def extract_metadata(file_path):
    data = _read_tags(file_path)
    if not data:
        return dict(EMPTY_METADATA)

    return {
        "title": data.get("Title"),
        "description": data.get("Caption-Abstract") or data.get("Description"),
        "date_taken": _parse_date(data.get("DateTimeOriginal")),
        "camera": data.get("Model"),
        "lens": data.get("LensModel"),
        "keywords": _as_list(data.get("Keywords")),
        "hierarchical_keywords": _as_list(data.get("HierarchicalSubject")),
    }


def _read_tags(file_path):
    try:
        result = subprocess.run(
            [EXIFTOOL_BIN, "-j", *TAGS, file_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return json.loads(result.stdout)[0]
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, IndexError):
        return {}


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None
