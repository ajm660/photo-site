from datetime import date

import cloudinary
from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )

    from app.routes.admin import admin_bp
    from app.routes.gallery import gallery_bp

    app.register_blueprint(gallery_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app import models  # noqa: F401  (registers models with SQLAlchemy)

    @app.context_processor
    def inject_site_details():
        return {
            "site_title": app.config["SITE_TITLE"],
            "site_owner": app.config["SITE_OWNER"],
            "contact_email": app.config["CONTACT_EMAIL"],
            "instagram_url": app.config["INSTAGRAM_URL"],
            "current_year": date.today().year,
        }

    return app
