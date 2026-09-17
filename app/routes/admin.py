import os
import tempfile
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from PIL import Image, UnidentifiedImageError
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models import Photo
from app.services import cloudinary_service, keyword_service, metadata_service

admin_bp = Blueprint("admin", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    password_hash = current_app.config["ADMIN_PASSWORD_HASH"]

    valid = (
        password_hash
        and username == current_app.config["ADMIN_USERNAME"]
        and check_password_hash(password_hash, password)
    )
    if not valid:
        flash("Incorrect username or password.", "error")
        return render_template("admin/login.html")

    session["admin_logged_in"] = True
    return redirect(request.form.get("next") or url_for("admin.upload"))


@admin_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("gallery.index"))


@admin_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("admin/upload.html")

    files = [f for f in request.files.getlist("photo") if f and f.filename]
    if not files:
        flash("Choose at least one photograph to upload.", "error")
        return render_template("admin/upload.html")

    confirmed = request.form.get("confirm_duplicate") == "1"

    if not confirmed:
        duplicate_filenames = [
            f.filename
            for f in files
            if Photo.query.filter_by(original_filename=f.filename).first()
        ]
        if duplicate_filenames:
            flash(
                "These filenames look like they may already be uploaded: "
                + ", ".join(duplicate_filenames)
                + ". Re-select your files and confirm below to upload anyway.",
                "warning",
            )
            return render_template(
                "admin/upload.html", duplicate_filenames=duplicate_filenames
            )

    uploaded, failed = [], []
    for file in files:
        filename = file.filename
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        try:
            if not _is_valid_image(tmp_path):
                failed.append(filename)
                continue

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
            uploaded.append(filename)
        except Exception:
            db.session.rollback()
            failed.append(filename)
        finally:
            os.unlink(tmp_path)

    if uploaded:
        flash(
            f"Uploaded {len(uploaded)} photograph(s): " + ", ".join(uploaded),
            "success",
        )
    if failed:
        flash(
            "Failed to upload (not a valid image, or an error occurred): "
            + ", ".join(failed),
            "error",
        )

    return redirect(url_for("gallery.index"))


@admin_bp.route("/sync", methods=["GET", "POST"])
@login_required
def sync():
    if request.method == "GET":
        return render_template("admin/sync.html")

    existing_ids = {
        row[0] for row in Photo.query.with_entities(Photo.cloudinary_public_id)
    }
    resources = cloudinary_service.list_folder_resources()
    new_resources = [r for r in resources if r["public_id"] not in existing_ids]

    synced, failed = [], []
    for resource in new_resources:
        public_id = resource["public_id"]
        try:
            image_metadata = cloudinary_service.get_image_metadata(public_id)
            metadata = metadata_service.extract_metadata_from_cloudinary(image_metadata)
            photo = Photo(
                cloudinary_public_id=public_id,
                original_filename=resource.get("original_filename"),
                title=metadata["title"],
                description=metadata["description"],
                width=resource.get("width"),
                height=resource.get("height"),
                date_taken=metadata["date_taken"],
                camera=metadata["camera"],
                lens=metadata["lens"],
                published=True,
            )
            db.session.add(photo)
            keyword_service.import_keywords(photo, metadata)
            db.session.commit()
            synced.append(public_id)
        except Exception:
            db.session.rollback()
            failed.append(public_id)

    if synced:
        flash(
            f"Synced {len(synced)} photograph(s) from Cloudinary: " + ", ".join(synced),
            "success",
        )
    if failed:
        flash("Failed to sync: " + ", ".join(failed), "error")
    if not synced and not failed:
        flash("No new photographs found in Cloudinary.", "success")

    return redirect(url_for("admin.sync"))


def _is_valid_image(path):
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except (UnidentifiedImageError, OSError):
        return False
