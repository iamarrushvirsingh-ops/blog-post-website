from flask import (Blueprint, render_template, abort, current_app, Response, request,
                   session, send_from_directory)
from sqlalchemy import or_
from blog.models import db, Post, Tag
from blog.utils import render_markdown, reading_time, avatar_svg

public = Blueprint("public", __name__)


def published():
    return Post.query.filter_by(status="published")  # drafts never show


@public.route("/")
def home():
    q = published()
    return render_template(
        "home.html",
        featured=q.filter_by(featured=True).order_by(Post.created_at.desc()).limit(3).all(),
        popular=q.order_by(Post.views.desc()).limit(4).all(),
        latest=q.order_by(Post.created_at.desc()).limit(6).all(),
    )


@public.route("/section/<slug>")
def section(slug):
    label = current_app.config["POST_TYPES"].get(slug) or abort(404)
    posts = published().filter_by(type=slug).order_by(Post.created_at.desc()).all()
    return render_template("list.html", heading=label, posts=posts)


@public.route("/tag/<name>")
def tag(name):
    posts = (published().filter(Post.tags.any(Tag.name == name.lower()))
             .order_by(Post.created_at.desc()).all())
    return render_template("list.html", heading="#" + name.lower(), posts=posts)


@public.route("/archive")
def archive():
    posts = published().order_by(Post.created_at.desc()).all()
    return render_template("list.html", heading="Archive", posts=posts)


@public.route("/post/<slug>")
def post(slug):
    p = Post.query.filter_by(slug=slug).first_or_404()
    live = p.status == "published"
    if not live and not session.get("admin"):
        abort(404)  # drafts are visible only to you
    if live and not session.get("admin"):
        p.views += 1  # your own visits are not counted
        db.session.commit()
    html, toc = render_markdown(p.body)
    return render_template("post.html", post=p, html=html, toc=toc,
                           minutes=reading_time(p.body))


@public.route("/avatar/<slug>.svg")
def avatar(slug):
    return Response(avatar_svg(slug[:220]), mimetype="image/svg+xml",
                    headers={"Cache-Control": "public, max-age=86400"})


@public.route("/uploads/<name>")
def uploaded(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)


@public.route("/search")
def search():
    q = request.args.get("q", "").strip()[:80]
    posts = []
    if q:
        posts = (published().filter(or_(
            Post.title.contains(q, autoescape=True), Post.summary.contains(q, autoescape=True),
            Post.body.contains(q, autoescape=True), Post.tags.any(Tag.name == q.lower())))
            .order_by(Post.created_at.desc()).all())
    return render_template("list.html", heading="Search", posts=posts, search=True, q=q)
