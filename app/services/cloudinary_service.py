"""All Cloudinary-specific code lives here.

The rest of the application should only call these functions and should
never reference the Cloudinary SDK directly. That keeps image storage
swappable for another provider (S3, R2, B2, ...) later.
"""

import cloudinary.api
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

UPLOAD_FOLDER = "photo-site"


def upload_photo(file):
    """Upload a file (path or file-like object) to Cloudinary.

    Returns the Cloudinary upload result dict, including public_id,
    width, height, format, etc.
    """
    return cloudinary.uploader.upload(file, folder=UPLOAD_FOLDER)


def list_folder_resources():
    """List every image in the photo-site asset folder via the Admin API,
    for syncing photos that were uploaded to Cloudinary directly rather
    than through the admin upload form.

    This account uses Cloudinary's dynamic folder mode, where an asset's
    folder is metadata (`asset_folder`) rather than a public_id prefix, so
    resources_by_asset_folder is used instead of a prefix-filtered listing.

    Note: this listing endpoint doesn't return embedded EXIF/IPTC/XMP data
    (even when asked for it) - fetch that per-resource via
    get_image_metadata().
    """
    resources = []
    cursor = None
    while True:
        kwargs = {"max_results": 500}
        if cursor:
            kwargs["next_cursor"] = cursor
        response = cloudinary.api.resources_by_asset_folder(UPLOAD_FOLDER, **kwargs)
        resources.extend(response.get("resources", []))
        cursor = response.get("next_cursor")
        if not cursor:
            break
    return resources


def get_image_metadata(public_id):
    """Fetch the embedded EXIF/IPTC/XMP metadata for a single resource.

    Cloudinary only returns this via the single-resource Admin API
    endpoint, not the folder/type listing endpoints, so this is one API
    call per asset - call it per-photo (not in a tight pre-fetch loop) so
    a single failure or rate limit doesn't block photos already synced.
    """
    detail = cloudinary.api.resource(public_id, image_metadata=True)
    return detail.get("image_metadata")


def delete_photo(public_id):
    return cloudinary.uploader.destroy(public_id)


def get_thumbnail_url(public_id):
    """Scaled to ~2x the gallery's target row height (for retina), full width
    preserved so the browser can crop it to fit the justified row via CSS
    object-fit — no server-side crop needed since the display box varies
    per photo/row width.
    """
    url, _ = cloudinary_url(
        public_id, height=520, crop="scale", quality="auto", fetch_format="auto"
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
