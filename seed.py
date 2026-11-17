"""Run once: python seed.py  -> creates the database and 6 sample posts."""
from datetime import datetime, timedelta
from app import app
from blog.models import db, Post, Tag
from blog.utils import slugify

CODE = "```bash\nnmap -sV -p- 10.10.10.10\n```"
SAMPLES = [
    ("Web App Pentest: Practice Lab Report", "reports", "Findings from an authorized lab test of a deliberately vulnerable app.", ["web-security", "ctf"], True, True, 120),
    ("How Prompt Injection Really Works", "articles", "A plain-language look at how LLMs get tricked, and how to defend them.", ["ai", "llm"], True, False, 340),
    ("Weekly AI Security Update", "weekly-ai-updates", "This week in AI security: new attacks, new defenses.", ["ai", "weekly"], False, False, 80),
    ("Monthly Tech Recap: November", "monthly-recaps", "The biggest security and tech stories of the month.", ["recap"], False, False, 60),
    ("Building a Port Scanner in Python", "projects", "A small project that finds open ports, step by step.", ["python", "networking"], True, False, 210),
    ("Notes on Adversarial Examples", "research-papers", "A short review of a paper on fooling image classifiers.", ["ai", "research"], False, False, 45),
]

with app.app_context():
    db.create_all()
    if Post.query.count():
        print("Database already has posts - nothing added.")
    for i, (title, typ, summary, tags, feat, sanit, views) in enumerate(SAMPLES if not Post.query.count() else []):
        body = f"This is a sample post. Replace it with your own.\n\n## Recon\n\nWe start with a scan:\n\n{CODE}\n\nOnly `ssh` and `http` were open.\n\n## Findings\n\nMore text goes here."
        p = Post(title=title, slug=slugify(title), summary=summary, body=body, type=typ,
                 status="published", featured=feat, sanitized=sanit, views=views,
                 created_at=datetime.now() - timedelta(days=i * 3))
        db.session.add(p)
        for name in tags:
            p.tags.append(Tag.query.filter_by(name=name).first() or Tag(name=name))
        db.session.add(p)
    db.session.commit()
    print("Done.")
