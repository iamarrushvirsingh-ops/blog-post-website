"""Run: python backup.py  -> saves a dated .zip of your database and uploads into the backups/ folder.
Copy that zip somewhere safe (another computer, cloud drive)."""
import os
import shutil
import sqlite3
from datetime import datetime
from app import app
from blog.models import db
import config

with app.app_context():
    db_path = db.engine.url.database
stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
folder = os.path.join(config.BASE_DIR, "backups", "latro-" + stamp)
os.makedirs(folder)
src, dst = sqlite3.connect(db_path), sqlite3.connect(os.path.join(folder, "blog.db"))
src.backup(dst)  # safe even while the site is running
src.close(); dst.close()
if os.path.isdir(config.UPLOAD_FOLDER):
    shutil.copytree(config.UPLOAD_FOLDER, os.path.join(folder, "uploads"))
shutil.make_archive(folder, "zip", folder)
shutil.rmtree(folder)
print("Backup saved:", folder + ".zip")
