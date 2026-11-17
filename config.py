import os
from dotenv import load_dotenv

load_dotenv()  # reads your private .env file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SITE_NAME = "LATRO"   # change the site name here, in one place
SITE_TAGLINE = "Security research, reports and weekly AI updates"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
PRODUCTION = os.environ.get("PRODUCTION") == "1"
ADMIN_PATH = os.environ.get("ADMIN_PATH", "latro-admin")  # your secret login address
SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"  # saved in the instance/ folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # uploads up to 10 MB
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = PRODUCTION
PERMANENT_SESSION_LIFETIME = 7200  # you are logged out after 2 hours

# slug -> label shown on the site
POST_TYPES = {
    "reports": "Reports",
    "articles": "Articles",
    "weekly-ai-updates": "Weekly AI Updates",
    "monthly-recaps": "Monthly Recaps",
    "projects": "Projects",
    "research-papers": "Research Papers",
}
