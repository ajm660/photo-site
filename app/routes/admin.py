import os
import tempfile

from flask import Blueprint, flash, redirect, render_template, request, url_for
from PIL import Image, UnidentifiedImageError

from app.extensions import db
from app.models import Photo
from app.services import cloudinary_service, keyword_service, metadata_service

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("admin/upload.html")

    file = request.files.get("photo")
    if not file or not file.filename:
        flash("Choose a photograph to upload.", "error")
        return render_template("admin/upload.html")

    filename = file.filename
    confirmed = request.form.get("confirm_duplicate") == "1"

    if not confirmed and Photo.query.filter_by(original_filename=filename).first():
        flash(
            f'"{filename}" looks like it may already be uploaded. '
            "Re-select the file and confirm below to upload anyway.",
            "warning",
        )
        return render_template("admin/upload.html", duplicate_filename=filename)

    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        if not _is_valid_image(tmp_path):
            flash("That file doesn't look like a valid image.", "error")
            return render_template("admin/upload.html")

        metadata = metadata_service.extract_metadata(tmp_path)
        upload_result = cloudinary_service.upload_photo(tmp_path)

        photo = Photo(
            cloudinary_public_id=upload_result["public_id"],
            original_filename=filename,
            title=metadata["title"],
            description=metadata["description"],
            width=upload_result.get("width"),
            height=upload_result.get("height"),
            date_taken=metadata["date_taken"],
            camera=metadata["camera"],
            lens=metadata["lens"],
            published=True,
        )
        db.session.add(photo)

        keyword_service.import_keywords(photo, metadata)

        db.session.commit()
    finally:
        os.unlink(tmp_path)

    flash(f'Uploaded "{filename}".', "success")
    return redirect(url_for("gallery.index"))


def _is_valid_image(path):
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except (UnidentifiedImageError, OSError):
        return False
