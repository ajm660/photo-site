import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace(
        "postgres://", "postgresql://", 1
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB upload limit

    SITE_TITLE = "Some Photographs"
    SITE_OWNER = "Andrew May"

    # Optional: the Contact page and its links only appear once one is set.
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
    INSTAGRAM_URL = os.environ.get("INSTAGRAM_URL")
