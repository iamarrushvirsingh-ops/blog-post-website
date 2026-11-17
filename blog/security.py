import os
import secrets
import time
from flask import current_app

_fails = {}  # who failed to log in, and when


def too_many(ip):  # 5 wrong tries in 15 minutes = locked out for a while
    now = time.time()
    _fails[ip] = [t for t in _fails.get(ip, []) if now - t < 900]
    return len(_fails[ip]) >= 5


def record_fail(ip):
    _fails.setdefault(ip, []).append(time.time())


def clear_fails(ip):
    _fails.pop(ip, None)


def save_upload(file, kind):
    """Saves an image or PDF under a random name, after checking what the file REALLY is
    (not just what its name says). Returns the new name, None if no file, or raises ValueError."""
    if not file or not file.filename:
        return None
    head = file.read(12)
    file.seek(0)
    ext = None
    if kind == "pdf" and head.startswith(b"%PDF"):
        ext = "pdf"
    elif kind == "image":
        if head.startswith(b"\x89PNG"):
            ext = "png"
        elif head.startswith(b"\xff\xd8\xff"):
            ext = "jpg"
        elif head.startswith(b"GIF8"):
            ext = "gif"
        elif head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            ext = "webp"
    if not ext:
        raise ValueError("Only real PNG, JPG, GIF or WEBP images and PDF files are allowed.")
    name = secrets.token_hex(16) + "." + ext
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], name))
    return name


def remove_upload(name):
    if name:
        try:
            os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], name))
        except OSError:
            pass
