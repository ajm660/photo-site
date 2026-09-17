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

    return _map_tags(data)


def extract_metadata_from_cloudinary(image_metadata):
    """Map the raw EXIF/IPTC/XMP dict returned by Cloudinary's
    `image_metadata` resource option into the same shape extract_metadata()
    produces from exiftool, so photos synced from Cloudinary get the same
    title/description/date/camera/lens/keyword handling as photos uploaded
    through the admin form.

    Cloudinary returns the same underlying tag names as exiftool, but
    repeatable fields (Keywords, HierarchicalSubject) may come back as a
    comma-joined string rather than a JSON array, so _as_list splits those.
    """
    if not image_metadata:
        return dict(EMPTY_METADATA)

    return _map_tags(image_metadata)


def _map_tags(data):
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
    if isinstance(value, str) and "," in value:
        return [v.strip() for v in value.split(",") if v.strip()]
    return [value]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None
