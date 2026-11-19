"""Make (or turn off) an owner's private edit link for the phone editor.

    python3 _tools/new_edit_link.py <slug> ["who it's for"]   make a link
    python3 _tools/new_edit_link.py --revoke <slug>          turn off every link for a site
    python3 _tools/new_edit_link.py --list                   show which sites have links

The link holds a random key. Only its SHA-256 goes into _tools/edit_keys.json,
so that file is safe in a public repo. Commit and push it; the editor API picks
up changes within a minute. The key itself is printed once and never stored:
text the link to the owner, and make a new one if they lose it.
"""
import hashlib
import json
import os
import secrets
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = os.path.join(HERE, "edit_keys.json")
EDITOR_URL = "https://tdeluise.github.io/lakehoustonwebco-demos/editor/"


def load():
    if not os.path.exists(KEYS):
        return {}
    return json.load(open(KEYS, encoding="utf-8"))


def save(keys):
    with open(KEYS, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=2, sort_keys=True)
        f.write("\n")


def main(argv):
    keys = load()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    if argv[0] == "--list":
        for h, v in sorted(keys.items(), key=lambda kv: kv[1]["slug"]):
            print(f'{v["slug"]:40} {v.get("created", ""):12} {v.get("label", "")}  ({h[:10]}…)')
        return 0
    if argv[0] == "--revoke":
        slug = argv[1]
        keep = {h: v for h, v in keys.items() if v["slug"] != slug}
        print(f"Turned off {len(keys) - len(keep)} link(s) for {slug}. Commit and push _tools/edit_keys.json.")
        save(keep)
        return 0

    slug = argv[0]
    if not os.path.exists(os.path.join(HERE, "sites", slug + ".json")):
        print(f"No _tools/sites/{slug}.json. Convert the site to a data file first.")
        return 1
    key = secrets.token_urlsafe(24)
    keys[hashlib.sha256(key.encode()).hexdigest()] = {
        "slug": slug,
        "label": argv[1] if len(argv) > 1 else "",
        "created": date.today().isoformat(),
    }
    save(keys)
    print(f"Edit link for {slug} (shown once, text it to the owner):\n\n  {EDITOR_URL}#k={key}\n")
    print("Then: git add _tools/edit_keys.json && git commit -m 'Edit link for " + slug + "' && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
