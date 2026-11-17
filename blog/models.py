from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.ForeignKey("post.id"), primary_key=True),
    db.Column("tag_id", db.ForeignKey("tag.id"), primary_key=True),
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    summary = db.Column(db.String(400), default="")
    body = db.Column(db.Text, default="")          # written in Markdown
    type = db.Column(db.String(40), nullable=False)  # a key of POST_TYPES
    status = db.Column(db.String(10), default="draft")  # draft / published
    featured = db.Column(db.Boolean, default=False)
    sanitized = db.Column(db.Boolean, default=False)  # "authorized / sanitized" badge
    cover_image = db.Column(db.String(200))
    pdf_file = db.Column(db.String(200))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.relationship("Tag", secondary=post_tags, backref="posts")


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)  # scrambled, never the real password
