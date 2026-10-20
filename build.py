#!/usr/bin/env python3
"""Fetch GitHub Trending (daily, all languages), merge with existing Chinese
summaries in data.json, save data.json and render index.html.

Usage:
  python3 build.py            # fetch trending + READMEs, update data.json, render
  python3 build.py --no-readme
Repos lacking Chinese summaries get empty zh fields; fill them in data.json
(keys: zh_tagline, zh_summary, zh_tags) then run `python3 render.py`.
"""
import json, os, re, sys, datetime, urllib.request
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
READMES = os.path.join(HERE, "readmes")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) trending-builder"}

def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def num(s):
    s = (s or "").strip().replace(",", "")
    m = re.search(r"\d+", s)
    return int(m.group()) if m else 0

def parse_trending(html):
    soup = BeautifulSoup(html, "html.parser")
    repos = []
    for i, art in enumerate(soup.select("article.Box-row"), 1):
        a = art.select_one("h2 a")
        path = a["href"].strip("/")
        owner, name = path.split("/", 1)
        desc_el = art.select_one("p")
        lang_el = art.select_one('[itemprop="programmingLanguage"]')
        color_el = art.select_one(".repo-language-color")
        color = None
        if color_el and color_el.get("style"):
            m = re.search(r"#[0-9a-fA-F]{3,8}", color_el["style"])
            color = m.group() if m else None
        stars = art.select_one(f'a[href="/{path}/stargazers"]')
        forks = art.select_one(f'a[href="/{path}/forks"]')
        today = art.select_one("span.d-inline-block.float-sm-right")
        repos.append({
            "rank": i, "owner": owner, "name": name, "full_name": path,
            "url": f"https://github.com/{path}",
            "description": desc_el.get_text(" ", strip=True) if desc_el else "",
            "language": lang_el.get_text(strip=True) if lang_el else None,
            "language_color": color,
            "stars": num(stars.get_text() if stars else ""),
            "forks": num(forks.get_text() if forks else ""),
            "stars_today": num(today.get_text() if today else ""),
        })
    return repos

def fetch_readme(full_name):
    os.makedirs(READMES, exist_ok=True)
    out = os.path.join(READMES, full_name.replace("/", "__") + ".md")
    for branch in ("HEAD", "main", "master"):
        for fn in ("README.md", "readme.md", "README.MD", "README.rst", "README"):
            try:
                txt = get(f"https://raw.githubusercontent.com/{full_name}/{branch}/{fn}", 20)
                open(out, "w").write(txt)
                return out
            except Exception:
                pass
    return None

def main():
    no_readme = "--no-readme" in sys.argv
    now = datetime.datetime.now(ZoneInfo("Asia/Shanghai"))
    repos = parse_trending(get("https://github.com/trending?since=daily"))
    old = {}
    if os.path.exists(DATA):
        for r in json.load(open(DATA)).get("repos", []):
            old[r["full_name"]] = r
    for r in repos:
        o = old.get(r["full_name"], {})
        r["zh_tagline"] = o.get("zh_tagline", "")
        r["zh_summary"] = o.get("zh_summary", "")
        r["zh_tags"] = o.get("zh_tags", [])
        if not no_readme:
            p = fetch_readme(r["full_name"])
            print(f"#{r['rank']:2} {r['full_name']}: readme={'ok' if p else 'missing'}")
    data = {"fetched_at": now.isoformat(timespec="seconds"),
            "fetched_at_display": now.strftime("%Y年%m月%d日 %H:%M"),
            "source": "https://github.com/trending?since=daily",
            "repos": repos}
    json.dump(data, open(DATA, "w"), ensure_ascii=False, indent=2)
    missing = [r["full_name"] for r in repos if not r["zh_summary"]]
    print(f"{len(repos)} repos saved to {DATA}; missing zh summaries: {len(missing)}")
    for m in missing: print("  -", m)
    import render; render.main()

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()
