"""All Cloudinary-specific code lives here.

The rest of the application should only call these functions and should
never reference the Cloudinary SDK directly. That keeps image storage
swappable for another provider (S3, R2, B2, ...) later.
"""

import cloudinary.uploader
from cloudinary.utils import cloudinary_url

UPLOAD_FOLDER = "photo-site"


def upload_photo(file):
    """Upload a file (path or file-like object) to Cloudinary.

    Returns the Cloudinary upload result dict, including public_id,
    width, height, format, etc.
    """
    return cloudinary.uploader.upload(file, folder=UPLOAD_FOLDER)


def delete_photo(public_id):
    return cloudinary.uploader.destroy(public_id)


def get_thumbnail_url(public_id):
    url, _ = cloudinary_url(
        public_id, width=700, crop="fill", quality="auto", fetch_format="auto"
    )
    return url


def get_gallery_url(public_id):
    url, _ = cloudinary_url(
        public_id, width=1000, crop="limit", quality="auto", fetch_format="auto"
    )
    return url


def get_large_url(public_id):
    url, _ = cloudinary_url(
        public_id, width=1800, crop="limit", quality="auto", fetch_format="auto"
    )
    return url
