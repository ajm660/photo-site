from flask import Blueprint, abort, render_template, request

from app.categories import PRIMARY_CATEGORIES, PRIMARY_CATEGORY_SLUG_SET, PRIMARY_CATEGORY_SLUGS
from app.models import Keyword, Photo

gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/")
def index():
    category_slug = request.args.get("category")
    if category_slug not in PRIMARY_CATEGORY_SLUG_SET:
        category_slug = None

    tag_slugs = [t for t in request.args.getlist("tags") if t]

    photos_query = Photo.query.filter_by(published=True)
    if category_slug:
        photos_query = photos_query.filter(Photo.keywords.any(Keyword.slug == category_slug))
    for slug in tag_slugs:
        photos_query = photos_query.filter(Photo.keywords.any(Keyword.slug == slug))

    photos = photos_query.order_by(Photo.date_taken.desc()).all()

    # Secondary filters are scoped to the selected category (or all published
    # photos, for "All") so the dropdown only ever shows tags that are
    # actually relevant, per spec §45's "Dynamic Secondary Filters".
    category_photos = Photo.query.filter_by(published=True)
    if category_slug:
        category_photos = category_photos.filter(Photo.keywords.any(Keyword.slug == category_slug))

    available_tags = (
        Keyword.query.join(Keyword.photos)
        .filter(Photo.id.in_(category_photos.with_entities(Photo.id)))
        .filter(~Keyword.slug.in_(PRIMARY_CATEGORY_SLUG_SET))
        .distinct()
        .order_by(Keyword.name)
        .all()
    )

    categories = [
        {"name": name, "slug": slug}
        for name, slug in zip(PRIMARY_CATEGORIES, PRIMARY_CATEGORY_SLUGS)
    ]

    photos_for_lightbox = [
        {"src": p.large_url, "title": p.title or p.original_filename} for p in photos
    ]

    return render_template(
        "gallery.html",
        photos=photos,
        categories=categories,
        selected_category=category_slug,
        available_tags=available_tags,
        selected_tags=set(tag_slugs),
        photos_for_lightbox=photos_for_lightbox,
    )


@gallery_bp.route("/photo/<int:photo_id>")
def photo_detail(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not photo.published:
        abort(404)
    return render_template("photo.html", photo=photo)
