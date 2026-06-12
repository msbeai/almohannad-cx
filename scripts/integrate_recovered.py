#!/usr/bin/env python3
"""Convert the 10 recovered LinkedIn articles (~/Downloads/cx-article-*.txt)
into Arabic content-collection files. These have no English translation yet,
so they are AR-only (the site already handles one-language articles)."""
import re
from pathlib import Path

DL = Path.home() / "Downloads"
OUT = Path.home() / "Projects" / "almohannad-cx" / "src" / "content" / "ar"

META = {
    "مهنة أبحاث السوق": ("market-research-as-a-profession", "Market Research as a Profession", "research"),
    "دليل وكالات أبحاث السوق في السعودية": ("market-research-agencies-directory-saudi-arabia", "Directory of Market Research Agencies in Saudi Arabia", "research"),
    "ترجمة لبرنامج التحكم بجودة الباحثين الميدانيين": ("field-researchers-quality-control-program", "Field Researchers Quality Control Program (Translated)", "research"),
    "أبحاث السوق أو أبحاث التسويق": ("market-research-or-marketing-research", "Market Research or Marketing Research?", "research"),
    "أفكار خدمية صغيرة لانطباعات إيجابية كبيرة": ("small-service-ideas-big-positive-impressions", "Small Service Ideas, Big Positive Impressions", "cx"),
    "نحو خدمة عملاء أفضل": ("toward-better-customer-service", "Toward Better Customer Service", "cx"),
    "الحوافز كوسيلة لرفع نسبة الاستجابة": ("incentives-to-raise-response-rates", "Incentives as a Way to Raise Response Rates", "research"),
    "لمحة تاريخية عن صناعة الأبحاث التسويقية": ("a-historical-glimpse-of-the-marketing-research-industry", "A Historical Glimpse of the Marketing Research Industry", "research"),
    "مؤشر جهد العميل | Customer effort score": ("customer-effort-score", "Customer Effort Score (CES)", "cx"),
    "هل يستحق مؤشر صافي الناصحين كل هذا التقدير؟": ("does-nps-deserve-all-this-praise", "Does NPS Deserve All This Praise?", "research"),
}

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}

def parse_date(raw):
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", raw.strip())
    if not m or m.group(1) not in MONTHS:
        return None
    return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"

def clean(body):
    # drop LinkedIn boilerplate footer lines
    drop = ("الآراء الواردة", "جميع مقالاتي المنشورة", "تابع صفحتي", "تابع صفحتي", "ملاحظة")
    out = []
    for block in body.split("\n\n"):
        b = block.strip()
        if not b or b in ("## .", "##"):
            continue
        if any(d in b for d in drop) and len(b) < 220:
            continue
        out.append(b.replace(" ", " "))
    return "\n\n".join(out).strip()

# next order numbers per theme
orders = {"cx": 0, "research": 0}
for f in OUT.glob("*.md"):
    t = f.read_text(encoding="utf-8")
    th = re.search(r"^theme: (\w+)", t, re.M).group(1)
    o = int(re.search(r"^order: (\d+)", t, re.M).group(1))
    orders[th] = max(orders[th], o)

count = 0
for src in sorted(DL.glob("cx-article-*.txt")):
    text = src.read_text(encoding="utf-8")
    m = re.match(r"TITLE: (.+)\nDATE: (.*)\nURL: (.*)\n---\n\n(.*)", text, re.S)
    title, date_raw, url, body = m.groups()
    title = title.strip()
    if title not in META:
        print("SKIP unknown:", title)
        continue
    slug, title_en, theme = META[title]
    if (OUT / f"{slug}.md").exists():
        print("exists:", slug)
        continue
    orders[theme] += 1
    date = parse_date(date_raw)
    fm = [
        f'title: "{title}"',
        f'titleAr: "{title}"',
        f'titleEn: "{title_en}"',
        f"theme: {theme}",
        f"order: {orders[theme]}",
        'linkedin: ""',
    ]
    if date:
        fm.append(f"date: {date}")
    (OUT / f"{slug}.md").write_text("---\n" + "\n".join(fm) + "\n---\n\n" + clean(body) + "\n", encoding="utf-8")
    count += 1
    print(f"added {slug} ({theme}, {date})")
print(f"\n{count} articles integrated")
