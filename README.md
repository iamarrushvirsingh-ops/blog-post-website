# LATRO

A personal cybersecurity blog with a built-in admin panel. One author, one login, no third-party CMS.

Publish weekly AI-and-security updates, reports, articles, projects, research papers and monthly tech recaps from a browser, and let visitors browse them by section, tag, search or archive.

> **Status:** All five stages are built (public site, admin panel, search and uploads, security hardening, About/Contact, RSS, deployment files). What remains is choosing a host and going live. See [DESIGN.md](DESIGN.md) for the full picture.

## Features

**For visitors**
- Home page with *Featured*, *Most popular* (real view counts) and *Latest* posts
- Six sections: Reports, Articles, Weekly AI Updates, Monthly Recaps, Projects, Research Papers
- Tag pages, a full archive, and search (title, summary, body, tags)
- Post pages with reading time, a "Sections" side card that follows your scroll, and an optional PDF download
- A "Sanitized / authorized" badge for reports
- About and Contact pages, an RSS feed (`/feed.xml`), a sitemap, themed error pages and link-preview tags
- Dark cyber theme with an animated starfield and a periodic logo glitch

**For the author (you)**
- Secret login address (you choose it)
- Dashboard: edit, publish/unpublish, delete
- Editor: Markdown with live preview, tags, cover image, PDF, Draft/Published, Featured flag
- Drafts are visible only to you, and your own visits are not counted in view numbers

## Tech stack

| Part | Tool |
|---|---|
| Server | Python, Flask |
| Database | SQLite (through Flask-SQLAlchemy) |
| Page templates | Jinja2 |
| Post format | Markdown, cleaned with bleach |
| Secrets | python-dotenv (`.env` file) |
| Front end | Plain CSS and JavaScript (no build step) |

## Quick start

You need Python 3.10 or newer.

```bash
git clone <your-repo-url>
cd latro

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then open .env and fill it in (see below)
python seed.py                    # optional: adds 6 sample posts
python create_admin.py            # creates your admin account
python app.py
```

Open `http://127.0.0.1:5000`. Your login page is at `http://127.0.0.1:5000/<ADMIN_PATH>/login`.

For auto-reload while developing, run with `FLASK_DEBUG=1 python app.py`. Never do this on a live server.

## Configuration

Private settings live in `.env` (never commit this file):

| Setting | What it does |
|---|---|
| `SECRET_KEY` | Long random string used to sign login sessions. Required when `PRODUCTION=1`. |
| `ADMIN_PATH` | The secret word in your login address, e.g. `blue-falcon` gives `/blue-falcon/login`. |
| `PRODUCTION` | `0` on your computer, `1` on the live server (turns on secure cookies and extra checks). |
| `DATA_DIR` | Folder on a **permanent disk** that will hold the database and uploads. Leave empty on your computer. |
| `PROXY_COUNT` | How many middlemen (proxies) sit in front of the site. Empty means 0 locally and 1 when `PRODUCTION=1`. |
| `CONTACT_EMAIL`, `GITHUB_URL`, `LINKEDIN_URL` | Shown on the Contact and About pages. Leave empty to hide. |

Public settings live in `config.py`: the site name (`SITE_NAME`), the tagline, and the list of post types.

Generate a good secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Writing a post

1. Log in and press **New post**.
2. Fill in the title, summary, type and tags (separate tags with commas).
3. Write the body in Markdown. Tips:
   - Use `## Heading` for sections. These build the "Sections" card on the post page automatically.
   - Use triple backticks for code boxes.
   - Show an image by linking to its address: `![description](https://...)`.
4. Optionally add a cover image (PNG, JPG, GIF, WEBP) and a PDF.
5. Choose **Draft** (hidden) or **Published**, then **Save**.

Tick **Sanitized / authorized report** only when the report is about a CTF, your own lab, or a test you had written permission to publish, with real names, IP addresses and sensitive details removed.

## Project structure

```
latro/
├── app.py               Starts the site; CSRF check and security headers
├── config.py            Settings and the list of post types
├── create_admin.py      Creates or resets the admin account
├── seed.py              Adds sample posts (only if the database is empty)
├── backup.py            Saves a dated .zip of the database and uploads
├── Procfile             Start command for hosts (gunicorn app:app)
├── gunicorn.conf.py     Production server settings
├── requirements.txt
├── .env.example         Template for your private .env
├── blog/
│   ├── models.py        Database tables: Post, Tag, Admin
│   ├── public_routes.py Pages visitors see
│   ├── admin_routes.py  Login, dashboard, editor
│   ├── security.py      Login lockout and safe uploads
│   └── utils.py         Slugs, reading time, Markdown cleaning, avatars
├── templates/           Page layouts (admin pages in templates/admin/)
├── static/              css/style.css and js/ (background, menu, contents card, admin, glitch)
├── instance/            Created automatically; holds blog.db (unless DATA_DIR is set)
├── uploads/             Created automatically; holds cover images and PDFs (unless DATA_DIR is set)
└── backups/             Created by backup.py
```

## Security summary

- Password stored as a hash, with a login lockout (5 wrong tries in 15 minutes)
- CSRF token on every form submission
- Post HTML cleaned with an allow-list, so scripts cannot run
- Uploads checked by real file type, saved under random names, 10 MB limit
- Content-Security-Policy, `nosniff`, no framing, same-origin referrer policy
- Secure, HTTP-only, same-site session cookies; 2-hour sessions
- Admin pages marked `noindex` and never cached
- App refuses to start with the default secret key when `PRODUCTION=1`

Found a problem? Please open an issue or contact the author privately before posting details publicly.

## Deploying

1. Pick a host that runs Python and offers a **permanent disk**. Without one, the database and uploads can be erased on restart.
2. Set the start command to `gunicorn app:app` (the included `Procfile` and `gunicorn.conf.py` already say this).
3. Set these environment variables on the host: `SECRET_KEY` (long random), `ADMIN_PATH` (your secret word), `PRODUCTION=1`, and `DATA_DIR` (a folder on the permanent disk). Optionally `CONTACT_EMAIL`, `GITHUB_URL`, `LINKEDIN_URL`.
4. Make sure the site is served over **HTTPS** (most hosts do this for free). In live mode the login cookie only works over HTTPS.
5. On the host, run `python create_admin.py` once to create your login. Do **not** run `seed.py`.
6. Edit the intro text in `templates/about.html`, then log in and write your first post.
7. Test: log in, write a post, upload a cover image and a PDF, publish, check that drafts stay hidden, and look at the site on your phone.

## Backups

Your whole blog is two things: the database (`blog.db`) and the `uploads/` folder. Run `python backup.py` to save both into one dated zip in `backups/`, then copy that zip somewhere safe on a schedule. Try restoring one at least once.

## Ethics

Only publish reports about systems you own, CTF/practice platforms, or targets where you have **written permission** to publish. Remove or anonymize names, IP addresses and anything sensitive.

## License

Not chosen yet. Add a `LICENSE` file (for example MIT) before making the repository public.
