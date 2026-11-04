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

    SITE_TITLE = "Andrew - photos"
    SITE_OWNER = "Andrew May"

    # Web3Forms delivers the Contact form to my inbox. This key is designed to
    # be public: it appears in the page source and doesn't reveal the address.
    WEB3FORMS_ACCESS_KEY = "4aaadc96-fcac-4f36-9bb4-489223d92b30"

    # Optional: shown as a link on the Contact page and in the footer.
    INSTAGRAM_URL = os.environ.get("INSTAGRAM_URL")
