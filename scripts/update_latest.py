"""Rewrite the README's LATEST block with the newest posts from ypro.dev's RSS feed."""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://ypro.dev/rss.xml"
COUNT = 5
START, END = "<!-- LATEST:START -->", "<!-- LATEST:END -->"

req = urllib.request.Request(FEED, headers={"User-Agent": "lavanut-profile-readme"})
with urllib.request.urlopen(req, timeout=30) as resp:
    root = ET.fromstring(resp.read())

lines = []
for item in root.findall("./channel/item")[:COUNT]:
    title = (item.findtext("title") or "").strip().replace("[", "(").replace("]", ")")
    link = (item.findtext("link") or "").strip()
    if not title or not link.startswith("https://ypro.dev/"):
        continue
    when = item.findtext("pubDate")
    date = parsedate_to_datetime(when).strftime("%b %-d, %Y") if when else ""
    lines.append(f"- [{title}]({link})" + (f" · {date}" if date else ""))

if not lines:
    sys.exit("No posts parsed from the feed; leaving README unchanged.")

readme = open("README.md", encoding="utf-8").read()
block = f"{START}\n" + "\n".join(lines) + f"\n{END}"
updated, n = re.subn(re.escape(START) + r".*?" + re.escape(END), block, readme, flags=re.S)
if n != 1:
    sys.exit("LATEST markers not found exactly once in README.md.")
open("README.md", "w", encoding="utf-8").write(updated)
print("\n".join(lines))
