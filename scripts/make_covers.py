#!/usr/bin/env python3
"""Generate unified-identity cover images (1200x630) for every article in both
languages, via the cover-template.html page rendered by headless Chrome.
Requires the dev server on :4321. Skips covers that already exist (delete
public/images/covers to regenerate everything, e.g. after a re-skin).
"""
import re, subprocess, sys
from pathlib import Path
from urllib.parse import quote

PROJECT = Path.home() / "Projects" / "almohannad-cx"
OUT = PROJECT / "public" / "images" / "covers"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
THEMES = {
    "cx": {"ar": "تجربة العميل", "en": "Customer Experience"},
    "research": {"ar": "الأبحاث التسويقية", "en": "Marketing Research"},
}

jobs = []
for lang in ("ar", "en"):
    for f in sorted((PROJECT / "src" / "content" / lang).glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = re.search(r'^title: "(.*?)"', text, re.M).group(1)
        theme = re.search(r"^theme: (\w+)", text, re.M).group(1)
        out = OUT / f"{f.stem}-{lang}.png"
        if out.exists():
            continue
        url = (
            "http://localhost:4321/cover-template.html"
            f"?t={quote(title)}&k={quote(THEMES[theme][lang])}&l={lang}"
        )
        jobs.append((out, url))

print(f"{len(jobs)} covers to generate", flush=True)
for i, (out, url) in enumerate(jobs, 1):
    subprocess.run(
        [CHROME, "--headless=new", f"--screenshot={out}", "--window-size=1200,630",
         "--hide-scrollbars", "--force-device-scale-factor=1",
         "--virtual-time-budget=4000", url],
        capture_output=True, timeout=60,
    )
    if not out.exists():
        print(f"FAILED: {out.name}", flush=True)
    if i % 25 == 0:
        print(f"{i}/{len(jobs)}", flush=True)
print("done", flush=True)
