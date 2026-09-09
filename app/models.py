from datetime import datetime

from app.extensions import db

photo_keywords = db.Table(
    "photo_keywords",
    db.Column("photo_id", db.Integer, db.ForeignKey("photos.id"), primary_key=True),
    db.Column("keyword_id", db.Integer, db.ForeignKey("keywords.id"), primary_key=True),
)


class Photo(db.Model):
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    cloudinary_public_id = db.Column(db.String(255), nullable=False, unique=True)
    original_filename = db.Column(db.String(255))

    title = db.Column(db.String(255))
    description = db.Column(db.Text)

    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    date_taken = db.Column(db.DateTime)

    camera = db.Column(db.String(255))
    lens = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    published = db.Column(db.Boolean, default=False, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)

    keywords = db.relationship(
        "Keyword", secondary=photo_keywords, back_populates="photos"
    )

    @property
    def thumbnail_url(self):
        from app.services import cloudinary_service

        return cloudinary_service.get_thumbnail_url(self.cloudinary_public_id)

    @property
    def gallery_url(self):
        from app.services import cloudinary_service

        return cloudinary_service.get_gallery_url(self.cloudinary_public_id)

    @property
    def large_url(self):
        from app.services import cloudinary_service

        return cloudinary_service.get_large_url(self.cloudinary_public_id)

    def __repr__(self):
        return f"<Photo {self.id} {self.cloudinary_public_id}>"


class Keyword(db.Model):
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True)

    parent_id = db.Column(db.Integer, db.ForeignKey("keywords.id"), nullable=True)
    parent = db.relationship("Keyword", remote_side=[id], back_populates="children")
    children = db.relationship("Keyword", back_populates="parent")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    photos = db.relationship(
        "Photo", secondary=photo_keywords, back_populates="keywords"
    )

    def __repr__(self):
        return f"<Keyword {self.slug}>"
