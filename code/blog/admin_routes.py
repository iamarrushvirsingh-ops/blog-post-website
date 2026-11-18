from functools import wraps
from flask import (Blueprint, render_template, request, redirect, url_for, session,
                   current_app, jsonify)
from werkzeug.security import check_password_hash
from blog.models import db, Post, Tag, Admin
from blog.utils import slugify, render_markdown
from blog.security import save_upload, remove_upload, too_many, record_fail, clear_fails

admin = Blueprint("admin", __name__)


def login_required(f):
    @wraps(f)
    def wrapper(*a, **k):
        if not session.get("admin"):
            return redirect(url_for("admin.login"))
        return f(*a, **k)
    return wrapper


def unique_slug(title):
    base = slugify(title) or "post"
    slug, n = base, 2
    while Post.query.filter_by(slug=slug).first():
        slug, n = f"{base}-{n}", n + 1
    return slug


@admin.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        ip = request.remote_addr
        if too_many(ip):
            error = "Too many wrong attempts. Try again in 15 minutes."
        else:
            u = Admin.query.filter_by(username=request.form.get("username", "")).first()
            if u and check_password_hash(u.password_hash, request.form.get("password", "")):
                clear_fails(ip)
                session.clear()
                session["admin"] = True
                session.permanent = True
                return redirect(url_for("admin.dashboard"))
            record_fail(ip)
            error = "Wrong username or password."
    return render_template("admin/login.html", error=error)


@admin.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.home"))


@admin.route("/")
@login_required
def dashboard():
    return render_template("admin/dashboard.html",
                           posts=Post.query.order_by(Post.updated_at.desc()).all())


@admin.route("/new", methods=["GET", "POST"])
@admin.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def editor(id=None):
    post = db.get_or_404(Post, id) if id else Post()
    f, posting, error = request.form, request.method == "POST", None
    if posting:
        title, typ, status = f.get("title", "").strip()[:200], f.get("type"), f.get("status")
        if not title:
            error = "Title is required."
        elif typ not in current_app.config["POST_TYPES"] or status not in ("draft", "published"):
            error = "Invalid type or status."
        img = pdf = None
        if not error:
            try:
                img = save_upload(request.files.get("cover"), "image")
                pdf = save_upload(request.files.get("pdf"), "pdf")
            except ValueError as e:
                remove_upload(img)
                error = str(e)
        if not error:
            post.title, post.type, post.status = title, typ, status
            post.summary, post.body = f.get("summary", "").strip()[:400], f.get("body", "")
            post.featured, post.sanitized = bool(f.get("featured")), bool(f.get("sanitized"))
            if img:
                remove_upload(post.cover_image)
                post.cover_image = img
            if pdf:
                remove_upload(post.pdf_file)
                post.pdf_file = pdf
            post.slug = post.slug or unique_slug(title)
            names = sorted({slugify(t) for t in f.get("tags", "").split(",")} - {""})[:8]
            post.tags = [Tag.query.filter_by(name=n).first() or Tag(name=n) for n in names]
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("admin.dashboard"))
    old = dict(title=post.title or "", summary=post.summary or "", body=post.body or "",
               type=post.type or "reports", status=post.status or "draft",
               tags=", ".join(t.name for t in post.tags))
    d = {k: f.get(k, v) if posting else v for k, v in old.items()}
    d["featured"] = bool(f.get("featured")) if posting else bool(post.featured)
    d["sanitized"] = bool(f.get("sanitized")) if posting else bool(post.sanitized)
    return render_template("admin/editor.html", post=post, d=d, error=error)


@admin.post("/toggle/<int:id>")
@login_required
def toggle(id):
    p = db.get_or_404(Post, id)
    p.status = "draft" if p.status == "published" else "published"
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin.post("/delete/<int:id>")
@login_required
def delete(id):
    p = db.get_or_404(Post, id)
    remove_upload(p.cover_image)
    remove_upload(p.pdf_file)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin.post("/preview")
@login_required
def preview():
    html, _ = render_markdown((request.get_json(silent=True) or {}).get("body", ""))
    return jsonify(html=html)
