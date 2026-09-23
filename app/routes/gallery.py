from flask import Blueprint, abort, render_template, request
from sqlalchemy import func

from app.categories import (
    ALL_CATEGORY_SLUG,
    ALL_PRIMARY_VARIANT_SLUGS,
    PRIMARY_CATEGORY_SHORT_NAMES,
    PRIMARY_CATEGORY_SLUGS,
    PRIMARY_CATEGORY_VARIANT_SLUGS,
    WEB_KEYWORD_SLUG,
)
from app.extensions import db
from app.models import Keyword, Photo

gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/")
def index():
    category_slug = request.args.get("category")
    if category_slug not in PRIMARY_CATEGORY_VARIANT_SLUGS:
        category_slug = ALL_CATEGORY_SLUG

    tag_slugs = [t for t in request.args.getlist("tags") if t]

    # Photos in the selected category (or, for "All", every web-published
    # photo) before any secondary keyword filter is applied — this is the
    # base set that keyword counts are computed against.
    category_photos = Photo.query.filter_by(published=True)
    if category_slug == ALL_CATEGORY_SLUG:
        category_photos = category_photos.filter(Photo.keywords.any(Keyword.slug == WEB_KEYWORD_SLUG))
    else:
        variant_slugs = PRIMARY_CATEGORY_VARIANT_SLUGS[category_slug]
        category_photos = category_photos.filter(Photo.keywords.any(Keyword.slug.in_(variant_slugs)))

    photos_query = category_photos
    for slug in tag_slugs:
        photos_query = photos_query.filter(Photo.keywords.any(Keyword.slug == slug))

    photos = photos_query.order_by(Photo.date_taken.desc()).all()

    category_photo_count = category_photos.count()

    categories = [{"name": "All", "slug": ALL_CATEGORY_SLUG, "short_name": "All"}] + [
        {"name": name, "slug": slug, "short_name": PRIMARY_CATEGORY_SHORT_NAMES.get(name, name)}
        for name, slug in PRIMARY_CATEGORY_SLUGS.items()
    ]

    # Every keyword occurring within the current category (excluding the
    # primary category keywords and the "web" publishing tag), with a count
    # of how many of that category's photos carry it — lets you refine
    # within a category (or across all of them) by a secondary keyword.
    keyword_counts = (
        db.session.query(Keyword, func.count(func.distinct(Photo.id)))
        .join(Keyword.photos)
        .filter(Photo.id.in_(category_photos.with_entities(Photo.id)))
        .filter(~Keyword.slug.in_(ALL_PRIMARY_VARIANT_SLUGS))
        .filter(Keyword.slug != WEB_KEYWORD_SLUG)
        .group_by(Keyword.id)
        .order_by(Keyword.name)
        .all()
    )
    all_keywords = [
        {"slug": keyword.slug, "name": keyword.name, "count": count}
        for keyword, count in keyword_counts
    ]
    selected_keyword = next(
        (kw for kw in all_keywords if kw["slug"] in tag_slugs), None
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
        selected_keyword=selected_keyword,
        all_keywords=all_keywords,
        category_photo_count=category_photo_count,
        photos_for_lightbox=photos_for_lightbox,
    )


@gallery_bp.route("/photo/<int:photo_id>")
def photo_detail(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not photo.published:
        abort(404)
    return render_template("photo.html", photo=photo)
