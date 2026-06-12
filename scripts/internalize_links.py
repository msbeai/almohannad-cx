#!/usr/bin/env python3
"""Rewrite in-body links that point to Almohannad's own LinkedIn articles so they
stay on the site. Operates directly on src/content (no vault access needed).
Citations to other people/sources are left untouched.
"""
import re, unicodedata
from pathlib import Path
from urllib.parse import unquote

PROJECT = Path.home() / "Projects" / "almohannad-cx"
DIRS = {"ar": PROJECT / "src" / "content" / "ar", "en": PROJECT / "src" / "content" / "en"}

def norm_tokens(s):
    s = unicodedata.normalize("NFC", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r"[^\w\s]", " ", s)
    return {w for w in s.split() if len(w) > 2}

# build url -> slug and title-token index from frontmatter
url_to_slug, title_index = {}, []
for f in DIRS["en"].glob("*.md"):
    text = f.read_text(encoding="utf-8")
    slug = f.stem
    m = re.search(r'linkedin: "(.*?)"', text)
    if m and m.group(1):
        url_to_slug[m.group(1).rstrip("/")] = slug
    t = re.search(r'titleAr: "(.*?)"', text)
    if t:
        title_index.append((norm_tokens(t.group(1)), slug))

def resolve(url):
    u = url.rstrip("/")
    if u in url_to_slug:
        return url_to_slug[u]
    if "linkedin" in u and ("/pulse/" in u or "/posts/" in u):
        words = norm_tokens(unquote(u).replace("-", " "))
        best, best_score = None, 0.0
        for tokens, slug in title_index:
            if tokens:
                score = len(tokens & words) / len(tokens)
                if score > best_score:
                    best, best_score = slug, score
        if best_score >= 0.8:
            return best
    return None

total = 0
for lang, d in DIRS.items():
    prefix = "/articles/" if lang == "ar" else "/en/articles/"
    for f in d.glob("*.md"):
        text = f.read_text(encoding="utf-8")
        fm_end = text.index("---", 4) + 3  # don't touch frontmatter
        head, body = text[:fm_end], text[fm_end:]
        count = [0]
        def repl(m):
            slug = resolve(m.group(2))
            if slug:
                count[0] += 1
                return f"[{m.group(1)}]({prefix}{slug})"
            return m.group(0)
        body = re.sub(r"\[([^\]]*)\]\((https?://[^)\s]+)\)", repl, body)
        if count[0]:
            f.write_text(head + body, encoding="utf-8")
            total += count[0]
print(f"internalized {total} links")
