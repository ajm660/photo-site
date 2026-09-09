from flask import Blueprint, abort, render_template, request

from app.categories import (
    ALL_PRIMARY_VARIANT_SLUGS,
    PRIMARY_CATEGORY_SLUGS,
    PRIMARY_CATEGORY_VARIANT_SLUGS,
)
from app.models import Keyword, Photo

gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/")
def index():
    category_slug = request.args.get("category")
    if category_slug not in PRIMARY_CATEGORY_VARIANT_SLUGS:
        category_slug = None

    tag_slugs = [t for t in request.args.getlist("tags") if t]

    photos_query = Photo.query.filter_by(published=True)
    if category_slug:
        variant_slugs = PRIMARY_CATEGORY_VARIANT_SLUGS[category_slug]
        photos_query = photos_query.filter(Photo.keywords.any(Keyword.slug.in_(variant_slugs)))
    for slug in tag_slugs:
        photos_query = photos_query.filter(Photo.keywords.any(Keyword.slug == slug))

    photos = photos_query.order_by(Photo.date_taken.desc()).all()

    categories = [
        {"name": name, "slug": slug} for name, slug in PRIMARY_CATEGORY_SLUGS.items()
    ]

    # Every keyword across all published photos, regardless of category —
    # lets you jump straight to a specific keyword without going through a
    # category first.
    all_keywords = (
        Keyword.query.join(Keyword.photos)
        .filter(Photo.published.is_(True))
        .filter(~Keyword.slug.in_(ALL_PRIMARY_VARIANT_SLUGS))
        .distinct()
        .order_by(Keyword.name)
        .all()
    )

    photos_for_lightbox = [
        {"src": p.large_url, "title": p.title or p.original_filename} for p in photos
    ]

    return render_template(
        "gallery.html",
        photos=photos,
        categories=categories,
        selected_category=category_slug,
        selected_tags=set(tag_slugs),
        all_keywords=all_keywords,
        photos_for_lightbox=photos_for_lightbox,
    )


@gallery_bp.route("/photo/<int:photo_id>")
def photo_detail(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not photo.published:
        abort(404)
    return render_template("photo.html", photo=photo)
