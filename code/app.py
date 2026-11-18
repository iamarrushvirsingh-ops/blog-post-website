import os
import hmac
import secrets
from datetime import datetime
from flask import Flask, session, request, abort, url_for, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import config
from blog.models import db
from blog.public_routes import public
from blog.admin_routes import admin

CSP = ("default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data: https:; "
       "script-src 'self'; frame-ancestors 'none'")


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    if config.PRODUCTION and config.SECRET_KEY == "dev-only-change-me":
        raise RuntimeError("Set a real SECRET_KEY in your .env before going live.")
    if config.PROXY_COUNT:  # trust the host's middleman so visitors' real addresses and https are seen
        n = config.PROXY_COUNT
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=n, x_proto=n, x_host=n)
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    db.init_app(app)
    app.register_blueprint(public)
    admin_prefix = "/" + config.ADMIN_PATH.strip("/")
    app.register_blueprint(admin, url_prefix=admin_prefix)
    with app.app_context():
        db.create_all()

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return session["csrf"]

    def thumb(p):  # your uploaded cover image, or an auto-made avatar
        if p.cover_image:
            return url_for("public.uploaded", name=p.cover_image)
        return url_for("public.avatar", slug=p.slug)

    @app.context_processor
    def site_info():
        return dict(site_name=config.SITE_NAME, tagline=config.SITE_TAGLINE,
                    post_types=config.POST_TYPES, year=datetime.now().year,
                    contact_email=config.CONTACT_EMAIL, github_url=config.GITHUB_URL,
                    linkedin_url=config.LINKEDIN_URL,
                    csrf_token=csrf_token, thumb=thumb)

    @app.before_request
    def check_csrf():  # every form submission must carry the secret token
        if request.method == "POST":
            sent = request.form.get("csrf") or request.headers.get("X-CSRF", "")
            token = session.get("csrf")
            if not token or not hmac.compare_digest(sent.encode(), token.encode()):
                abort(400)

    @app.after_request
    def security_headers(r):
        r.headers["Content-Security-Policy"] = CSP
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["X-Frame-Options"] = "DENY"
        r.headers["Referrer-Policy"] = "same-origin"
        if request.path.startswith(admin_prefix):
            r.headers["Cache-Control"] = "no-store"
        return r

    def error_page(e):
        code = getattr(e, "code", 500)
        msgs = {400: "Bad request", 404: "Page not found", 413: "That file is too large",
                500: "Something went wrong on our side"}
        return render_template("error.html", code=code, msg=msgs.get(code, "Error")), code
    for code in (400, 404, 413, 500):
        app.register_error_handler(code, error_page)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
