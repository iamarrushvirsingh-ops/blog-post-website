from datetime import timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape
from flask import (Blueprint, url_for, render_template, abort, current_app, Response, request,
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


@public.route("/about")
def about():
    return render_template("about.html")


@public.route("/contact")
def contact():
    return render_template("contact.html")


@public.route("/feed.xml")
def feed():
    """RSS feed: lets people follow your posts in a reader app."""
    posts = published().order_by(Post.created_at.desc()).limit(20).all()
    items = "".join(
        "<item><title>%s</title><link>%s</link><guid>%s</guid><pubDate>%s</pubDate>"
        "<description>%s</description></item>" % (
            escape(p.title), url_for("public.post", slug=p.slug, _external=True),
            url_for("public.post", slug=p.slug, _external=True),
            format_datetime(p.created_at.replace(tzinfo=timezone.utc)), escape(p.summary or ""))
        for p in posts)
    xml = ('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
           "<title>%s</title><link>%s</link><description>%s</description>%s</channel></rss>" % (
               escape(current_app.config["SITE_NAME"]), url_for("public.home", _external=True),
               escape(current_app.config["SITE_TAGLINE"]), items))
    return Response(xml, mimetype="application/rss+xml")


@public.route("/sitemap.xml")
def sitemap():
    urls = [url_for(e, _external=True) for e in ("public.home", "public.archive", "public.about", "public.contact")]
    urls += [url_for("public.section", slug=s, _external=True) for s in current_app.config["POST_TYPES"]]
    urls += [url_for("public.post", slug=p.slug, _external=True) for p in published().all()]
    xml = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + "".join("<url><loc>%s</loc></url>" % escape(u) for u in urls) + "</urlset>")
    return Response(xml, mimetype="application/xml")


@public.route("/robots.txt")
def robots():
    body = "User-agent: *\nAllow: /\nSitemap: %s\n" % url_for("public.sitemap", _external=True)
    return Response(body, mimetype="text/plain")
