"""Run once: python create_admin.py  -> makes your admin account (run again to change the password)."""
import getpass
from werkzeug.security import generate_password_hash
from app import app
from blog.models import db, Admin

with app.app_context():
    username = input("Admin username: ").strip()
    pw = getpass.getpass("Password (at least 12 characters): ")
    if len(pw) < 12 or pw != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords must match and be at least 12 characters.")
    a = Admin.query.first() or Admin()
    a.username, a.password_hash = username, generate_password_hash(pw)
    db.session.add(a)
    db.session.commit()
    print("Saved. Log in at /" + app.config["ADMIN_PATH"].strip("/") + "/login")
