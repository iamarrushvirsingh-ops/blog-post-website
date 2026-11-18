# LATRO: Design Document

## 1. Purpose

A personal blog for one cybersecurity author to publish weekly AI-and-security updates, reports on targets (CTF, lab, authorized tests), articles, projects, research papers and monthly recaps. The author writes and manages posts through a private admin panel in the browser. Visitors read, browse and search.

### Goals
- Single author, simple to run, easy to read and change
- Publish from the browser, with drafts and a live preview
- Browse by section, tag, archive and search
- A home page that surfaces featured, popular and recent posts
- A strong security baseline, since this is a security blog
- A distinctive dark "cyber" look

### Non-goals (for now)
- Multiple authors or user accounts for readers
- Comments, newsletters, social login
- A plugin or theme system
- High-traffic scaling

## 2. Key decisions

| Decision | Choice | Why |
|---|---|---|
| Static site or dynamic | **Dynamic** (Flask + database) | The author wants to write posts in a browser, LinkedIn-style, with an admin login. |
| Language/framework | **Flask** | The author already knows Python and Flask, so the code stays readable and changeable. |
| Database | **SQLite** | One file, no server to run, plenty for a single-author blog. |
| Post format | **Markdown**, cleaned with bleach | Easy to write, good for code blocks, and cleaning removes harmful HTML. |
| Admin accounts | **One admin** | Only the author posts for now. |
| Popularity | **Real view counts** | The server can count visits, so "Most popular" is genuine. |
| Front end | **Plain CSS/JS, no build step** | Fewer moving parts, easy to deploy. |
| Dark theme only | Yes | Matches the reference look. A light mode can be added later. |
| Forms protection | **Hand-written CSRF check** | Avoids an extra dependency; small and easy to audit. |

## 3. Architecture

```
Browser
   |
   v
Flask app (app.py)
   |-- before_request: CSRF check on every POST
   |-- after_request:  security headers
   |-- public blueprint  (blog/public_routes.py)  -> visitor pages
   |-- admin blueprint   (blog/admin_routes.py)   -> mounted at /<ADMIN_PATH>
   v
SQLite (instance/blog.db)  +  uploads/ folder (images, PDFs)
```

- **App factory:** `create_app()` in `app.py` loads settings, registers the two blueprints, creates tables and uploads folder.
- **Public blueprint:** read-only pages, search, avatars, and file serving.
- **Admin blueprint:** login, dashboard, editor, publish toggle, delete, Markdown preview. All pages except login require the logged-in session.
- **Templates:** `base.html` provides the top bar, footer, background canvas and scripts; other pages extend it.
- **Scripts:** each in its own file (no inline scripts), so the Content-Security-Policy can forbid them.

## 4. Data model

**Post**: `id`, `title`, `slug` (unique), `summary`, `body` (Markdown), `type` (one of the configured post types), `status` (`draft` or `published`), `featured`, `sanitized`, `cover_image`, `pdf_file`, `views`, `created_at`, `updated_at`

**Tag**: `id`, `name` (unique, lowercase)

**post_tags**: links posts and tags (many-to-many)

**Admin**: `id`, `username` (unique), `password_hash`

Notes:
- The slug is made from the title once and then kept, so links do not break when a title is edited.
- Tags are normalized to lowercase slug form and limited to 8 per post.
- Post types are defined in `config.py` (`POST_TYPES`), not in the database.

## 5. Routes

**Public**

| Route | Purpose |
|---|---|
| `/` | Home: featured (3), most popular (4), latest (6) |
| `/section/<slug>` | All published posts of one type |
| `/tag/<name>` | All published posts with a tag |
| `/archive` | All published posts, newest first |
| `/search?q=` | Search title, summary, body and tag |
| `/post/<slug>` | One post. Counts a view (not for the admin). Drafts return 404 unless the admin is logged in. |
| `/avatar/<slug>.svg` | Generated pixel avatar for a post |
| `/uploads/<name>` | Serves uploaded images and PDFs |
| `/about`, `/contact` | Static pages; email and social links come from `.env` |
| `/feed.xml` | RSS feed of the 20 newest posts |
| `/sitemap.xml`, `/robots.txt` | For search engines |

**Admin** (all under `/<ADMIN_PATH>`)

| Route | Purpose |
|---|---|
| `/login` (GET, POST) | Log in |
| `/logout` (POST) | Log out |
| `/` | Dashboard |
| `/new`, `/edit/<id>` | Create or edit a post |
| `/toggle/<id>` (POST) | Publish or unpublish |
| `/delete/<id>` (POST) | Delete a post and its files |
| `/preview` (POST) | Returns cleaned HTML for the live preview |

## 6. Main flows

**Reading a post:** request, look up the published post, add 1 to its views (unless admin), convert Markdown to HTML, clean it, build the contents list from `##` headings, render the page.

**Publishing a post:** log in, open the editor, fill the form, optionally upload files, press Save. The server validates the title, type and status, checks upload file types, creates a unique slug if new, saves tags, and writes to the database. Published posts appear on all listing pages immediately.

**Logging in:** the form carries a CSRF token. Failed attempts are counted per IP address. After 5 failures in 15 minutes, login is refused for that period. A successful login clears the old session and starts a new 2-hour session.

## 7. Security design

| Threat | Defense |
|---|---|
| Guessing the admin password | Hashed password, 12+ character minimum at creation, lockout after 5 failures |
| Finding the admin page | Secret, configurable `ADMIN_PATH`; admin pages marked `noindex` and never cached |
| Forged form submissions (CSRF) | Per-session token required on every POST (form field or `X-CSRF` header), compared in constant time |
| Script injection (XSS) via posts | Markdown output cleaned with an allow-list of tags, attributes and link types |
| Script injection via other routes | Content-Security-Policy: scripts only from the site itself, no inline scripts, no framing |
| Malicious uploads | File type checked by real file signature (not name), random file names, 10 MB limit |
| Path tricks when serving files | Files served with Flask's safe file-sending helper |
| Session theft | HTTP-only, same-site cookies; Secure flag in production; 2-hour lifetime |
| Weak production setup | App refuses to start in production with the default secret key |
| Clickjacking, MIME sniffing | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` |

## 8. Visual design

- **Colors:** background `#050b16`, panels `#08111f`, cyan `#00e5ff` (main), red `#ff1744` (accent), green `#76e600` (badges), text `#c3d0de`
- **Fonts:** Orbitron (headings, labels), Rajdhani (body), Share Tech Mono (code and tags)
- **Background:** full-screen canvas of drifting, twinkling dots joined by faint lines; speed set by `SPEED` in `bg.js`; paused for visitors who prefer reduced motion
- **Top bar:** logo and name on the left; HOME, SECTIONS (dropdown), ARCHIVE, SEARCH, ADMIN (when logged in) on the right, with a sliding underline on hover
- **Logo:** glitch animation 3 seconds after load and then every 30 to 60 seconds; turns red on hover
- **Cards:** avatar (or cover image) plus type, title, summary, tags and date; the whole card is clickable
- **Post page:** large avatar, summary and info lines, code boxes with a colored side stripe, a sticky "Sections" card that marks the current heading with `[x]`
- **Accessibility:** keyboard focus outlines, reduced-motion support, labelled form fields

## 9. Deployment design

- **Server:** gunicorn (`Procfile`, `gunicorn.conf.py`). One worker with four threads, so the in-memory login lockout counter lives in one place.
- **Proxy fix:** hosts put a proxy in front of the app. With `PROXY_COUNT` set (default 1 when `PRODUCTION=1`), the app reads the visitor's real IP address and the HTTPS setting from the proxy, so lockouts and secure links work correctly.
- **Permanent storage:** `DATA_DIR` moves the database and uploads onto a mounted permanent disk. Left empty, they stay in the project folder.
- **Backups:** `backup.py` makes a safe dated zip of the database and uploads.
- **Error pages:** themed pages for 400, 404, 413 and 500 so visitors never see raw framework errors.
- **SEO and sharing:** page descriptions, Open Graph tags (cover image used when present), sitemap, robots.txt, favicon, RSS.

## 10. Known limitations

1. **Login lockout is stored in memory.** It resets on restart and only works correctly with a single worker process (the default config).
2. **Storage depends on the host.** The database and uploads need a permanent disk (`DATA_DIR`). Hosts without one will lose them.
3. **No database migrations.** Tables are created automatically, but changing a table later needs a migration tool or manual changes.
4. **View counts are simple.** Each page load counts, including refreshes and bots.
5. **No pagination.** Listing pages show every matching post.
6. **Single admin and no password-reset page.** Re-run `create_admin.py` to change the password.
7. **Images in post bodies are links only.** There is no upload-and-insert button.
8. **External fonts.** Google Fonts are loaded from Google's servers.
9. **No contact form.** The Contact page shows an email link instead, to avoid spam and abuse.
10. **Not yet reviewed in all browsers** or by an independent security tester.

## 11. Roadmap

**Before launch (your part)**
- Choose a host with a permanent disk, then set the environment variables and run `create_admin.py` there
- Edit `templates/about.html` with your own introduction
- Test in real browsers and on a phone

**Later ideas**
- Light mode toggle
- Pagination
- Insert-image button in the editor
- Shared storage for login lockout if more than one worker is needed
- Database migrations
- Optional analytics, newsletter or comments
- Multiple authors with roles

## 12. Open questions

- Which host? It must run Flask, offer a permanent disk, and be reachable and affordable from India.
- Custom domain name?
- Final site name (LATRO is a placeholder; change `SITE_NAME` in `config.py`).
