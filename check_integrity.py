import os
import re

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

ids = re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", html)
missing = [i for i in set(ids) if f'id="{i}"' not in html and f"id='{i}'" not in html]
print("Missing DOM IDs in index.html:", missing)

# Check all classes or references in script
onclicks = re.findall(r"onclick=[\"']([^\"']+)[\"']", html)
print("Inline onclicks:", len(onclicks))
for oc in onclicks:
    print(" -", oc[:60])
