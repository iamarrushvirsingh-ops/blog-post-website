import re
import bleach
import markdown

# Only these tags/attributes survive in a post; anything else (like <script>) is made harmless
TAGS = ["p", "br", "hr", "h2", "h3", "h4", "strong", "em", "del", "ul", "ol", "li", "blockquote",
        "pre", "code", "a", "img", "table", "thead", "tbody", "tr", "th", "td"]
ATTRS = {"a": ["href", "title"], "img": ["src", "alt"], "code": ["class"],
         "h2": ["id"], "h3": ["id"], "h4": ["id"]}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def reading_time(text):
    return max(1, round(len((text or "").split()) / 200))


def render_markdown(body):
    """Turn Markdown text into HTML, plus a list of ## headings for the Sections card."""
    md = markdown.Markdown(extensions=["fenced_code", "tables", "toc"],
                           extension_configs={"toc": {"toc_depth": "2"}})
    html = bleach.clean(md.convert(body or ""), tags=TAGS, attributes=ATTRS,
                        protocols=["http", "https", "mailto"])
    return html, md.toc_tokens


def avatar_svg(seed):
    """A unique 5x5 pixel avatar for each post, made from its slug (same slug = same picture)."""
    import hashlib
    d = hashlib.sha256(seed.encode()).digest()
    color = ["#00e5ff", "#ff1744", "#76e600"][d[0] % 3]
    cells = ""
    for row in range(5):
        for col in range(3):
            if d[1 + row * 3 + col] % 2:
                for cx in {col, 4 - col}:
                    cells += f'<rect x="{14 + cx * 14}" y="{14 + row * 14}" width="12" height="12" fill="{color}"/>'
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 98 98">'
            '<rect width="98" height="98" fill="#08111f"/>' + cells + '</svg>')
