from flask import Blueprint, abort, render_template, request
from sqlalchemy import false

from app.models import Keyword, Photo

gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/")
def index():
    keyword_slug = request.args.get("keyword")

    query = Photo.query.filter_by(published=True)
    selected_keyword = None
    if keyword_slug:
        selected_keyword = Keyword.query.filter_by(slug=keyword_slug).first()
        if selected_keyword:
            query = query.filter(Photo.keywords.any(Keyword.slug == keyword_slug))
        else:
            query = query.filter(false())

    photos = query.order_by(Photo.date_taken.desc()).all()

    keywords = (
        Keyword.query.join(Keyword.photos)
        .filter(Photo.published.is_(True))
        .distinct()
        .order_by(Keyword.name)
        .all()
    )

    return render_template(
        "gallery.html", photos=photos, keywords=keywords, selected_keyword=keyword_slug
    )


@gallery_bp.route("/photo/<int:photo_id>")
def photo_detail(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not photo.published:
        abort(404)
    return render_template("photo.html", photo=photo)
