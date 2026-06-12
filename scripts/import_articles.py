#!/usr/bin/env python3
"""Import Almohannad's articles from the Obsidian vault into Astro content collections.

Arabic source : one big export (articles.md) with <a id="art_N"></a> anchors
English source: per-article .md files with `source-anchor: art_N` frontmatter
Pairing key   : art_N
"""
import re, json, shutil, unicodedata
from pathlib import Path

VAULT = Path("/Users/almohannad/Documents/Obsidian Vault/CX Knowledge")
AR_SOURCE = VAULT / "مقالاتي على لنكد إن - md" / "articles.md"
AR_MEDIA = VAULT / "مقالاتي على لنكد إن - md" / "media"
EN_DIRS = {
    "cx": VAULT / "Articles" / "Customer Experience",
    "research": VAULT / "Articles" / "Marketing Research and Metrics",
}
PROJECT = Path.home() / "Projects" / "almohannad-cx"
OUT_AR = PROJECT / "src" / "content" / "ar"
OUT_EN = PROJECT / "src" / "content" / "en"
OUT_IMG = PROJECT / "public" / "images" / "articles"

for d in (OUT_AR, OUT_EN, OUT_IMG):
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)

ar_text = AR_SOURCE.read_text(encoding="utf-8")

# ---- index table: anchor -> (linkedin url, date) -----------------------------
index = {}
for m in re.finditer(
    r"\|\s*\d+\s*\|\s*\[\*\*(.+?)\*\*\]\(#(art_\d+)\)\s*\|\s*\[عرض ↗\]\((\S+?)\)\s*\|\s*(.*?)\s*\|",
    ar_text,
):
    title, anchor, url, date = m.groups()
    index[anchor] = {"linkedin": url, "date": None if date in ("—", "-", "") else date}

# ---- split Arabic body by anchors --------------------------------------------
ar_articles = {}
parts = re.split(r'<a id="(art_\d+)"></a>', ar_text)
# parts: [preamble, anchor1, body1, anchor2, body2, ...]
for i in range(1, len(parts) - 1, 2):
    anchor, body = parts[i], parts[i + 1]
    # body starts with "## title"
    mt = re.match(r"\s*##\s+(.+?)\s*\n", body)
    if not mt:
        continue
    title = mt.group(1).strip()
    content = body[mt.end():]
    # cut at any top-level section heading that belongs to the export, not the article
    content = re.split(r"\n#\s+\*?\*?(?:أولًا|ثانيًا|ثالثًا)", content)[0]
    ar_articles[anchor] = {"title": title, "body": content.strip()}

# ---- extra (unanchored) articles: locate by Arabic title line ----------------
def find_extra_body(title_ar):
    """Slice an unanchored article: from its standalone title line to the next boundary."""
    lines = ar_text.splitlines(keepends=True)
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().rstrip("؟?") == title_ar.strip().rstrip("؟?") and i > 100:  # skip index table
            start = i + 1
            break
    if start is None:
        return None
    out = []
    for ln in lines[start:]:
        s = ln.strip()
        if s.startswith('<a id="art_') or re.match(r"^#\s", s) or s.startswith("*      *"):
            break
        if s and extra_titles and s.rstrip("؟?") in extra_titles and s.rstrip("؟?") != title_ar.strip().rstrip("؟?"):
            break
        out.append(ln)
    return "".join(out).strip()

# dates/urls for LinkedIn-only table rows (direct links, no anchor)
extra_index = {}
for m in re.finditer(
    r"\|\s*\d+\s*\|\s*\[\*\*(.+?)\*\*\]\((http\S+?)\)\s*.*?\|\s*\[عرض ↗\]\(\S+?\)\s*\|\s*(.*?)\s*\|",
    ar_text,
):
    title, url, date = m.groups()
    extra_index[title.strip()] = {"linkedin": url, "date": None if date in ("—", "-", "") else date}

# ---- English files ------------------------------------------------------------
def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
        text = text[m.end():]
    return fm, text

def slugify(title):
    s = unicodedata.normalize("NFKD", title)
    s = re.sub(r"[''']", "", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January","February","March","April","May","June","July","August","September","October","November","December"])}
MONTHS.update({m[:3]: i + 1 for m, i in [(k, v - 1) for k, v in MONTHS.items()]})

def parse_date(raw):
    if not raw:
        return None
    m = re.match(r"([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})", raw.strip())
    if not m:
        return None
    mon = MONTHS.get(m.group(1)) or MONTHS.get(m.group(1)[:3])
    if not mon:
        return None
    return f"{m.group(3)}-{mon:02d}-{int(m.group(2)):02d}"

def clean_en_body(text):
    # drop the H1 and the "Originally published" callout
    text = re.sub(r"^\s*#\s.+\n", "", text, count=1)
    text = re.sub(r"^\s*>\s*Originally published.*\n", "", text, count=1, flags=re.M)
    # obsidian image embeds -> markdown images
    text = re.sub(r"!\[\[([^\]]+?)\]\]", r"![](/images/articles/\1)", text)
    # wiki links -> plain text (keep alias if present)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+?)\]\]", r"\1", text)
    return text.strip()

def clean_ar_body(text):
    # markdown images with relative media path -> public path
    text = re.sub(r"!\[[^\]]*\]\(media/([^)]+)\)", r"![](/images/articles/\1)", text)
    text = re.sub(r"!\[\[([^\]]+?)\]\]", r"![](/images/articles/\1)", text)
    # promote common standalone section labels to headings
    for label in ("تمهيد", "في الختام", "الخاتمة", "ختاما", "ختامًا"):
        text = re.sub(rf"^\s*\*?\*?{label}\*?\*?\s*$", f"## {label}", text, flags=re.M)
    return text.strip()

def yaml_quote(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

records = []
warnings = []
# collect extra titles first (for boundary detection)
extra_titles = set()
for theme, d in EN_DIRS.items():
    for f in d.glob("*.md"):
        if f.name.endswith("MOC.md"):
            continue
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm.get("source-anchor") == "extra" and fm.get("arabic-title"):
            extra_titles.add(fm["arabic-title"].strip().rstrip("؟?"))

for theme, d in EN_DIRS.items():
    for f in sorted(d.glob("*.md")):
        if f.name.endswith("MOC.md"):
            continue
        fm, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        anchor = fm.get("source-anchor")
        order = int(re.match(r"(\d+)", f.name).group(1))
        title_en = fm.get("english-title") or f.stem.split(" - ", 1)[-1]
        title_ar = fm.get("arabic-title", "")
        ar = ar_articles.get(anchor)
        meta = index.get(anchor, {})
        if not ar and anchor == "extra" and title_ar:
            body_ar = find_extra_body(title_ar)
            if body_ar:
                ar = {"title": title_ar, "body": body_ar}
                meta = extra_index.get(title_ar.strip(), {})
        if not ar:
            # English translation exists but Arabic original is LinkedIn-only
            ar = {"title": title_ar, "body": None}
        slug = slugify(title_en)
        date = parse_date(meta.get("date"))
        records.append({
            "slug": slug, "theme": theme, "order": order,
            "titleAr": title_ar or ar["title"], "titleEn": title_en,
            "date": date, "linkedin": fm.get("linkedin-url") or meta.get("linkedin"),
            "bodyAr": clean_ar_body(ar["body"]) if ar["body"] else None,
            "bodyEn": clean_en_body(body),
        })

# ---- internalize links to his own articles -------------------------------------
def norm_title(s):
    s = unicodedata.normalize("NFC", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r"[^\w\s]", " ", s)
    return [w for w in s.split() if len(w) > 2]

url_to_slug = {}
title_tokens = []
for r in records:
    if r["linkedin"]:
        url_to_slug[r["linkedin"].rstrip("/")] = r["slug"]
    title_tokens.append((set(norm_title(r["titleAr"])), r["slug"]))

from urllib.parse import unquote

def resolve_internal(url):
    u = url.rstrip("/")
    if u in url_to_slug:
        return url_to_slug[u]
    if "linkedin" in u and ("/pulse/" in u or "/posts/" in u):
        decoded = unquote(u).replace("-", " ")
        words = set(norm_title(decoded))
        best, best_score = None, 0.0
        for tokens, slug in title_tokens:
            if not tokens:
                continue
            score = len(tokens & words) / len(tokens)
            if score > best_score:
                best, best_score = slug, score
        if best_score >= 0.8:
            return best
    return None

def internalize_links(body, lang):
    prefix = "/articles/" if lang == "ar" else "/en/articles/"
    def repl(m):
        slug = resolve_internal(m.group(2))
        return f"[{m.group(1)}]({prefix}{slug})" if slug else m.group(0)
    return re.sub(r"\[([^\]]*)\]\((https?://[^)\s]+)\)", repl, body)

internalized = 0
for r in records:
    for key, lang in (("bodyAr", "ar"), ("bodyEn", "en")):
        if r[key]:
            new = internalize_links(r[key], lang)
            internalized += len(re.findall(r"\]\(/(?:en/)?articles/", new)) - len(re.findall(r"\]\(/(?:en/)?articles/", r[key]))
            r[key] = new
print(f"internalized links: {internalized}")

# ---- write content files -------------------------------------------------------
used_images = set()
for r in records:
    for body in (r["bodyAr"], r["bodyEn"]):
        if body:
            used_images.update(re.findall(r"/images/articles/([^)\s]+)", body))
    common = [
        f"titleAr: {yaml_quote(r['titleAr'])}",
        f"titleEn: {yaml_quote(r['titleEn'])}",
        f"theme: {r['theme']}",
        f"order: {r['order']}",
        f"linkedin: {yaml_quote(r['linkedin'] or '')}",
    ]
    if r["date"]:
        common.append(f"date: {r['date']}")
    if r["bodyAr"]:
        (OUT_AR / f"{r['slug']}.md").write_text(
            "---\n" + f"title: {yaml_quote(r['titleAr'])}\n" + "\n".join(common) + "\n---\n\n" + r["bodyAr"] + "\n",
            encoding="utf-8")
    (OUT_EN / f"{r['slug']}.md").write_text(
        "---\n" + f"title: {yaml_quote(r['titleEn'])}\n" + "\n".join(common) + "\n---\n\n" + r["bodyEn"] + "\n",
        encoding="utf-8")

copied = 0
for img in sorted(used_images):
    src = AR_MEDIA / img
    if src.exists():
        shutil.copy2(src, OUT_IMG / img)
        copied += 1
    else:
        warnings.append(f"missing image {img}")

print(f"articles: {len(records)} (cx={sum(1 for r in records if r['theme']=='cx')}, research={sum(1 for r in records if r['theme']=='research')})")
print(f"images copied: {copied}/{len(used_images)}")
print(f"dated: {sum(1 for r in records if r['date'])}")
for w in warnings:
    print("WARN:", w)
