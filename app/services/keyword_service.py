from slugify import slugify

from app.extensions import db
from app.models import Keyword


def get_or_create_keyword(name, parent=None):
    """Find an existing keyword by slug (case-insensitive) or create it."""
    slug = slugify(name)
    keyword = Keyword.query.filter_by(slug=slug).first()
    if keyword:
        return keyword

    keyword = Keyword(name=name.strip(), slug=slug, parent=parent)
    db.session.add(keyword)
    return keyword


def assign_keywords(photo, keyword_names):
    """Get-or-create each keyword name and attach it to the photo."""
    for name in keyword_names:
        if not name or not name.strip():
            continue
        keyword = get_or_create_keyword(name)
        if keyword not in photo.keywords:
            photo.keywords.append(keyword)


def _assign_hierarchical(photo, path):
    """Walk a Lightroom hierarchical keyword path (e.g. "Place|UK|Leicester"),
    creating the parent chain, and attach only the leaf keyword to the photo.
    """
    parent = None
    leaf = None
    for name in path.split("|"):
        name = name.strip()
        if not name:
            continue
        leaf = get_or_create_keyword(name, parent=parent)
        parent = leaf

    if leaf and leaf not in photo.keywords:
        photo.keywords.append(leaf)


def import_keywords(photo, metadata):
    """Attach the keywords found by metadata_service.extract_metadata to a photo.

    Hierarchical keywords (Lightroom's HierarchicalSubject) build a parent
    chain and attach the leaf. Flat keywords not already covered by a
    hierarchical path are attached as root-level keywords.
    """
    hierarchical_paths = metadata.get("hierarchical_keywords", [])
    for path in hierarchical_paths:
        _assign_hierarchical(photo, path)

    leaves_from_hierarchy = {
        path.split("|")[-1].strip().lower() for path in hierarchical_paths
    }
    flat_names = [
        name
        for name in metadata.get("keywords", [])
        if name.strip().lower() not in leaves_from_hierarchy
    ]
    assign_keywords(photo, flat_names)
