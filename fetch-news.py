import feedparser
import json
from datetime import datetime, timezone

FEEDS = [
    {
        "url":      "https://www.pymnts.com/feed/",
        "source":   "PYMNTS",
        "cssClass": "source-pymnts",
        "count":    3,
    },
    {
        "url":      "https://www.finextra.com/rss/headlines.aspx",
        "source":   "Finextra",
        "cssClass": "source-finextra",
        "count":    3,
    },
]

def parse_date(entry):
    """Return a nicely formatted date string from a feed entry."""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                dt = datetime(*t[:6], tzinfo=timezone.utc)
                return dt.strftime("%b %-d, %Y")
            except Exception:
                pass
    return ""

def clean_html(text):
    """Strip HTML tags from a string."""
    import re
    return re.sub(r"<[^>]+>", "", text or "").strip()

articles = []

for feed_cfg in FEEDS:
    try:
        feed = feedparser.parse(feed_cfg["url"])
        entries = feed.entries[: feed_cfg["count"]]
        for entry in entries:
            title = clean_html(entry.get("title", ""))
            link  = entry.get("link", "#")
            date  = parse_date(entry)
            desc  = clean_html(
                entry.get("summary", "") or entry.get("description", "")
            )
            if len(desc) > 160:
                desc = desc[:160].rsplit(" ", 1)[0] + "\u2026"
            articles.append({
                "title":    title,
                "link":     link,
                "date":     date,
                "desc":     desc,
                "source":   feed_cfg["source"],
                "cssClass": feed_cfg["cssClass"],
            })
        print(f"  {feed_cfg['source']}: fetched {len(entries)} articles")
    except Exception as e:
        print(f"  {feed_cfg['source']}: ERROR — {e}")

# Interleave: PYMNTS, Finextra, PYMNTS, Finextra ...
pymnts   = [a for a in articles if a["source"] == "PYMNTS"]
finextra = [a for a in articles if a["source"] == "Finextra"]
interleaved = []
for i in range(max(len(pymnts), len(finextra))):
    if i < len(pymnts):   interleaved.append(pymnts[i])
    if i < len(finextra): interleaved.append(finextra[i])

output = {
    "updated": datetime.now(timezone.utc).strftime("%b %-d, %Y at %H:%M UTC"),
    "articles": interleaved,
}

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(interleaved)} articles to news.json")
print(f"Last updated: {output['updated']}")
