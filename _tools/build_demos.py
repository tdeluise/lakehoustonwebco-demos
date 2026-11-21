"""Lake Houston Web Co demo generator.

Builds one static, phone-first page per business from real public facts only.
Each business is one file: _tools/sites/<slug>.json. Owners change their own file
through the phone editor (editor/ + editor-api/); a GitHub Action then rebuilds.

Usage: python3 build_demos.py <output_root> [slug ...]   (no slugs = build all)
       python3 build_demos.py <output_root> some/data.json  (a file with one business or a list)

Per-business switches in the JSON:
  "launched": true  -> the client's real, live site: search engines may index it,
                       and the footer shows a "Website by Lake Houston Web Co" credit.
  "credit": false   -> on a launched site, leave the credit off (owner said no).

Owner-editable extras (all optional):
  "notice":   {"text": "Closed today for a family event", "until": "2026-11-20"}
              banner under the header; hidden automatically after "until" (Central time).
  "specials": [{"title": "Taco Tuesday", "text": "3 for $5", "price": "$5"}]
  "photos":   [{"src": "assets/owner-1.jpg", "alt": "Fresh birria tacos"}]
"""
import glob
import html
import json
import os
import sys
from datetime import date

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
FOOTER = "Demo site prepared by Lake Houston Web Co"
SITE = "https://lakehoustonwebco.com/"


def footer_line(b):
    if not b.get("launched"):
        return f'<p class="demo">{FOOTER}</p>'
    if b.get("credit") is False:
        return ""
    return f'<p class="demo">Website by <a href="{SITE}" style="color: inherit">Lake Houston Web Co</a></p>'


THEMES = {
    # name: (display font, body font, google fonts query, palette)
    "barber": dict(
        display="'Oswald', 'Arial Narrow', sans-serif",
        body="'Work Sans', system-ui, sans-serif",
        fonts="family=Oswald:wght@500;600;700&family=Work+Sans:wght@400;500;600",
        bg="#f4f1ea", surface="#fffdf8", ink="#1b1a17", muted="#5f5a50",
        accent="#9b2c22", accent2="#1f3a5f", band="#1b1a17", band_ink="#f4f1ea",
        motif="pole",
    ),
    "rugged": dict(
        display="'Alfa Slab One', Georgia, serif",
        body="'Work Sans', system-ui, sans-serif",
        fonts="family=Alfa+Slab+One&family=Work+Sans:wght@400;500;600",
        bg="#efe8dc", surface="#fbf7f0", ink="#231d16", muted="#62574a",
        accent="#8a4b14", accent2="#2f4a3a", band="#231d16", band_ink="#efe8dc",
        motif="plank",
    ),
    "salon": dict(
        display="'Cormorant Garamond', Georgia, serif",
        body="'Mulish', system-ui, sans-serif",
        fonts="family=Cormorant+Garamond:wght@500;600;700&family=Mulish:wght@400;500;600;700",
        bg="#f7f1ee", surface="#ffffff", ink="#2a1e24", muted="#6c5a62",
        accent="#7b3b5a", accent2="#b8866b", band="#2a1e24", band_ink="#f7f1ee",
        motif="arc",
    ),
    "taqueria": dict(
        display="'Alfa Slab One', Georgia, serif",
        body="'Work Sans', system-ui, sans-serif",
        fonts="family=Alfa+Slab+One&family=Work+Sans:wght@400;500;600;700",
        bg="#fbf3e4", surface="#fffaf1", ink="#2b1a12", muted="#6e5747",
        accent="#c2410c", accent2="#0f766e", band="#7c2d12", band_ink="#fff3dd",
        motif="picado",
    ),
    "burger": dict(
        display="'Rye', Georgia, serif",
        body="'Work Sans', system-ui, sans-serif",
        fonts="family=Rye&family=Work+Sans:wght@400;500;600;700",
        bg="#f6efe0", surface="#fffaf0", ink="#221a14", muted="#5f5246",
        accent="#b02a1e", accent2="#6b4f00", band="#221a14", band_ink="#f6efe0",
        motif="check",
    ),
    "mariscos": dict(
        display="'Alfa Slab One', Georgia, serif",
        body="'Work Sans', system-ui, sans-serif",
        fonts="family=Alfa+Slab+One&family=Work+Sans:wght@400;500;600;700",
        bg="#eef6f6", surface="#ffffff", ink="#0e2a33", muted="#4b6670",
        accent="#e4572e", accent2="#0b6e7a", band="#0b3b4a", band_ink="#e9f6f4",
        motif="wave",
    ),
    "bakery": dict(
        display="'Fredoka', 'Arial Rounded MT Bold', sans-serif",
        body="'Nunito Sans', system-ui, sans-serif",
        fonts="family=Fredoka:wght@500;600;700&family=Nunito+Sans:wght@400;600;700",
        bg="#fdf3ec", surface="#ffffff", ink="#3a2418", muted="#7a5f50",
        accent="#d9466f", accent2="#e8a33d", band="#5a3322", band_ink="#fdf3ec",
        motif="sprinkle",
    ),
    "diner": dict(
        display="'Bree Serif', Georgia, serif",
        body="'Work Sans', system-ui, sans-serif",
        fonts="family=Bree+Serif&family=Work+Sans:wght@400;500;600;700",
        bg="#eef4f1", surface="#ffffff", ink="#17262a", muted="#4f6266",
        accent="#c8452f", accent2="#1f6f6a", band="#17262a", band_ink="#eef4f1",
        motif="stripe",
    ),
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def e(s):
    return html.escape(str(s), quote=True)


def motif_css(m, t):
    if m == "pole":
        return f"repeating-linear-gradient(135deg, {t['accent']} 0 14px, #fff 14px 28px, {t['accent2']} 28px 42px, #fff 42px 56px)"
    if m == "plank":
        return f"repeating-linear-gradient(90deg, {t['accent']} 0 60px, #6f3c10 60px 62px)"
    if m == "arc":
        return f"radial-gradient(circle at 10px -4px, transparent 12px, {t['accent2']} 13px 15px, transparent 16px) 0 0/28px 14px repeat-x"
    if m == "picado":
        return (f"linear-gradient(135deg, transparent 50%, {t['bg']} 50%) 0 0/24px 14px repeat-x, "
                f"repeating-linear-gradient(90deg, {t['accent']} 0 48px, {t['accent2']} 48px 96px, #e9a81c 96px 144px, #be185d 144px 192px)")
    if m == "wave":
        return (f"radial-gradient(circle at 12px 0, transparent 11px, {t['accent2']} 12px 14px, transparent 15px) 0 0/24px 12px repeat-x, "
                f"linear-gradient({t['band']}, {t['band']})")
    if m == "sprinkle":
        return (f"radial-gradient(circle at 6px 7px, {t['accent']} 2.5px, transparent 3px) 0 0/22px 14px repeat-x, "
                f"radial-gradient(circle at 17px 7px, {t['accent2']} 2.5px, transparent 3px) 0 0/22px 14px repeat-x, "
                f"linear-gradient({t['band']}, {t['band']})")
    if m == "stripe":
        return f"repeating-linear-gradient(90deg, {t['accent']} 0 28px, {t['surface']} 28px 34px, {t['accent2']} 34px 62px, {t['surface']} 62px 68px)"
    if m == "check":
        return f"repeating-conic-gradient({t['accent']} 0 25%, #fffaf0 0 50%) 0 0/14px 14px"
    return t["accent"]


def tel(p):
    d = "".join(ch for ch in p if ch.isdigit())
    return "+1" + d if len(d) == 10 else ("+" + d if d else "")


def maps(addr):
    from urllib.parse import quote
    return "https://www.google.com/maps/search/?api=1&query=" + quote(addr)


def notice_html(b):
    n = b.get("notice") or {}
    if not n.get("text"):
        return ""
    until = n.get("until", "")
    if until:
        try:
            if date.fromisoformat(until) < date.today():
                return ""  # expired at build time; the script below also hides it in the browser
        except ValueError:
            until = ""
    attr = f' data-until="{e(until)}"' if until else ""
    return f'<div class="notice" role="status"{attr}><p>{e(n["text"])}</p></div>'


def specials_html(b):
    sp = [x for x in b.get("specials") or [] if x.get("title")]
    if not sp:
        return ""
    cards = []
    for x in sp:
        price = f'<span class="price">{e(x["price"])}</span>' if x.get("price") else ""
        text = f"<p>{e(x['text'])}</p>" if x.get("text") else ""
        cards.append(f'<div class="special"><h3>{e(x["title"])}{price}</h3>{text}</div>')
    return f'<section class="wrap" id="specials"><h2>Specials</h2><div class="specials">{"".join(cards)}</div></section>'


def photos_html(b):
    ph = [x for x in b.get("photos") or [] if str(x.get("src", "")).startswith("assets/")]
    if not ph:
        return ""
    imgs = "".join(f'<img src="{e(x["src"])}" alt="{e(x.get("alt", ""))}" loading="lazy">' for x in ph)
    return f'<section class="wrap" id="photos"><h2>Photos</h2><div class="photos">{imgs}</div></section>'


EXTRA_CSS = {
    "notice": ".notice {{ background: var(--accent); color:#fff; }} .notice p {{ max-width:1040px; margin:0 auto; padding: 12px 18px; font-weight:700; font-size:1.05rem; }}",
    "specials": ".specials {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }} .special {{ background: var(--surface); border-radius:12px; padding:16px 18px; border-top:5px solid var(--accent2); }} .special h3 {{ display:flex; justify-content:space-between; gap:12px; font-size:1.25rem; }} .special .price {{ color: var(--accent); white-space:nowrap; }} .special p {{ margin:0; }}",
    "photos": ".photos {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap:10px; }} .photos img {{ width:100%; aspect-ratio: 1; object-fit: cover; border-radius:10px; display:block; }}",
}

NOTICE_JS = """
(function () {
  try {
    var t = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Chicago" }).format(new Date());
    document.querySelectorAll(".notice[data-until]").forEach(function (n) { if (n.getAttribute("data-until") < t) n.remove(); });
  } catch (err) {}
})();"""


def page(b):
    t = THEMES[b["theme"]]
    name = b["name"]
    phone = b.get("phone", "")
    addr = b.get("address", "")
    locs = b.get("locations") or ([{"label": "", "address": addr, "phone": phone, "hours": b.get("hours")}] if addr else [])
    rating = b.get("rating")
    ctas = []
    if phone:
        ctas.append(f'<a class="btn primary" href="tel:{tel(phone)}">Call {e(phone)}</a>')
    if locs:
        ctas.append(f'<a class="btn" href="{e(maps(locs[0]["address"]))}" target="_blank" rel="noopener">Get directions</a>')
    if b.get("facebook"):
        ctas.append(f'<a class="btn" href="{e(b["facebook"])}" target="_blank" rel="noopener">Facebook</a>')

    rating_html = ""
    if rating:
        count = f' · {e(rating["count"])} reviews' if rating.get("count") else ""
        n = max(0, min(5, round(float(rating["value"]))))
        stars = "★" * n + "☆" * (5 - n)
        rating_html = f'<p class="rating"><span class="stars" aria-hidden="true">{stars}</span> <b>{e(rating["value"])}</b> on {e(rating["source"])}{count}</p>'

    about = "".join(f"<p>{e(p)}</p>" for p in b.get("about", []))
    items_html = ""
    if b.get("items"):
        groups = b["items"]
        blocks = []
        for g in groups:
            lis = "".join(f"<li>{e(i)}</li>" for i in g["list"])
            head = f"<h3>{e(g['title'])}</h3>" if g.get("title") else ""
            blocks.append(f'<div class="group">{head}<ul>{lis}</ul></div>')
        note = f'<p class="fine">{e(b["items_note"])}</p>' if b.get("items_note") else ""
        items_html = f'''<section class="wrap" id="menu"><h2>{e(b.get("items_title", "Menu"))}</h2><div class="groups">{"".join(blocks)}</div>{note}</section>'''

    loc_html = []
    for L in locs:
        rows = ""
        if L.get("hours"):
            rows = "".join(
                f'<tr data-day="{i}"><th scope="row">{d}</th><td>{e(L["hours"].get(d, "Not listed"))}</td></tr>'
                for i, d in enumerate(DAYS)
            )
            rows = f'<table class="hours"><tbody>{rows}</tbody></table>'
        elif L.get("hours_note"):
            rows = f'<p>{e(L["hours_note"])}</p>'
        ph = f'<p><a href="tel:{tel(L["phone"])}">{e(L["phone"])}</a></p>' if L.get("phone") else ""
        label = f"<h3>{e(L['label'])}</h3>" if L.get("label") else ""
        loc_html.append(f'''<div class="loc">{label}<p class="addr">{e(L["address"])}</p>{ph}
<p><a href="{e(maps(L["address"]))}" target="_blank" rel="noopener">Open in Google Maps ↗</a></p>{rows}</div>''')
    hours_note = f'<p class="fine">{e(b["hours_source"])}</p>' if b.get("hours_source") else ""
    visit = f'<section class="wrap" id="visit"><h2>{e(b.get("visit_title", "Hours & location"))}</h2><div class="locs">{"".join(loc_html)}</div>{hours_note}</section>' if loc_html else ""

    rev_html = ""
    if b.get("reviews"):
        cards = "".join(
            f'<figure><blockquote>“{e(r["text"])}”</blockquote><figcaption>— {e(r["name"])}{(", " + e(r["where"])) if r.get("where") else ""}</figcaption></figure>'
            for r in b["reviews"]
        )
        rev_html = f'<section class="wrap" id="reviews"><h2>What people say</h2><p class="fine">Quoted from public reviews. First names only.</p><div class="reviews">{cards}</div></section>'

    notice = notice_html(b)
    specials = specials_html(b)
    photos = photos_html(b)
    extra_css = "".join("\n" + EXTRA_CSS[k].replace("{{", "{").replace("}}", "}") for k, v in (("notice", notice), ("specials", specials), ("photos", photos)) if v)
    extra_js = NOTICE_JS if notice else ""

    nav = []
    if specials:
        nav.append('<a href="#specials">Specials</a>')
    if b.get("items"):
        nav.append(f'<a href="#menu">{e(b.get("items_nav", "Menu"))}</a>')
    if visit:
        nav.append('<a href="#visit">Hours</a>')
    if rev_html:
        nav.append('<a href="#reviews">Reviews</a>')
    head_cta = f'<a class="pill" href="tel:{tel(phone)}">Call</a>' if phone else (f'<a class="pill" href="{e(maps(locs[0]["address"]))}" target="_blank" rel="noopener">Directions</a>' if locs else "")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{"" if b.get("launched") else '<meta name="robots" content="noindex, nofollow">'}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} — {e(b["city"])}, {e(b.get("st","TX"))}</title>
<meta name="description" content="{e(b["tagline"])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{t["fonts"]}&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{t["bg"]}; --surface:{t["surface"]}; --ink:{t["ink"]}; --muted:{t["muted"]}; --accent:{t["accent"]}; --accent2:{t["accent2"]}; --band:{t["band"]}; --band-ink:{t["band_ink"]}; --display:{t["display"]}; --body:{t["body"]}; }}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.6 var(--body); }}
a {{ color: var(--accent); }}
h1,h2,h3 {{ font-family: var(--display); line-height:1.05; margin:0 0 .5rem; text-wrap: balance; }}
.top {{ position: sticky; top:0; z-index:5; background: var(--band); color: var(--band-ink); }}
.top .in {{ max-width: 1040px; margin:0 auto; padding: 10px 18px; display:flex; align-items:center; justify-content:space-between; gap:12px; }}
.brand {{ font-family: var(--display); font-size: 1.15rem; color: var(--band-ink); text-decoration:none; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.top nav {{ display:flex; gap:16px; align-items:center; }}
.top nav a {{ color: var(--band-ink); text-decoration:none; font-weight:600; font-size:.95rem; opacity:.9; }}
.pill {{ background: var(--accent); color:#fff !important; padding: 7px 14px; border-radius: 999px; opacity:1 !important; }}
.motif {{ height: 14px; background: {motif_css(t["motif"], t)}; }}
.hero {{ max-width:1040px; margin:0 auto; padding: 56px 18px 44px; }}
.eyebrow {{ text-transform: uppercase; letter-spacing:.14em; font-size:.8rem; font-weight:700; color: var(--accent2); margin:0 0 12px; }}
.hero h1 {{ font-size: clamp(2.6rem, 9vw, 5.2rem); }}
.tag {{ font-size: clamp(1.1rem, 3.4vw, 1.4rem); color: var(--muted); max-width: 34ch; margin: .4rem 0 1.4rem; }}
.rating {{ margin: 0 0 1.4rem; font-size: 1rem; }}
.stars {{ color: #e2a400; letter-spacing: 2px; }}
.ctas {{ display:flex; flex-wrap:wrap; gap:10px; }}
.btn {{ display:inline-flex; align-items:center; min-height:46px; padding: 10px 18px; border-radius: 10px; border: 2px solid var(--ink); color: var(--ink); text-decoration:none; font-weight:700; }}
.btn.primary {{ background: var(--accent); border-color: var(--accent); color:#fff; }}
.wrap {{ max-width:1040px; margin:0 auto; padding: 40px 18px; border-top: 1px solid color-mix(in srgb, var(--ink) 12%, transparent); }}
.wrap h2 {{ font-size: clamp(1.8rem, 5vw, 2.6rem); margin-bottom: 1rem; }}
.about p {{ max-width: 62ch; font-size: 1.08rem; }}
.groups {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }}
.group {{ background: var(--surface); border-radius: 14px; padding: 18px 20px; box-shadow: 0 1px 0 color-mix(in srgb, var(--ink) 10%, transparent); }}
.group h3 {{ font-size: 1.25rem; color: var(--accent); }}
.group ul {{ margin:0; padding-left: 1.1rem; }}
.group li {{ margin: .25rem 0; }}
.fine {{ color: var(--muted); font-size: .88rem; margin-top: 1rem; }}
.locs {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 22px; }}
.loc {{ background: var(--surface); border-radius: 14px; padding: 20px; }}
.loc h3 {{ font-size: 1.3rem; }}
.addr {{ font-weight: 600; font-size: 1.08rem; margin: 0 0 .3rem; }}
.hours {{ width:100%; border-collapse: collapse; margin-top: .8rem; font-variant-numeric: tabular-nums; }}
.hours th, .hours td {{ text-align:left; padding: 7px 4px; border-bottom: 1px dashed color-mix(in srgb, var(--ink) 18%, transparent); }}
.hours th {{ font-weight: 600; width: 42%; }}
.hours tr.today {{ background: color-mix(in srgb, var(--accent) 12%, transparent); }}
.hours tr.today th::after {{ content: " · today"; color: var(--accent); font-weight: 700; }}
.reviews {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; }}
figure {{ margin:0; background: var(--surface); border-left: 5px solid var(--accent); border-radius: 12px; padding: 18px 20px; }}
blockquote {{ margin:0 0 .6rem; font-size: 1.08rem; }}
figcaption {{ color: var(--muted); font-weight: 600; }}
.foot {{ background: var(--band); color: var(--band-ink); text-align:center; padding: 30px 18px 36px; }}
.foot p {{ margin: .3rem 0; }}
.foot .demo {{ opacity:.8; font-size:.9rem; margin-top: 1rem; }}
@media (max-width: 560px) {{ .top nav a:not(.pill) {{ display:none; }} .hero {{ padding-top: 36px; }} }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}{extra_css}
</style>
</head>
<body>
<header class="top"><div class="in"><a class="brand" href="#">{e(b.get("short", name))}</a><nav>{"".join(nav)}{head_cta}</nav></div></header>
<div class="motif" aria-hidden="true"></div>{notice}
<main>
<section class="hero">
<p class="eyebrow">{e(b["eyebrow"])}</p>
<h1>{e(name)}</h1>
<p class="tag">{e(b["tagline"])}</p>
{rating_html}
<div class="ctas">{"".join(ctas)}</div>
</section>
<section class="wrap about" id="about"><h2>{e(b.get("about_title", "About"))}</h2>{about}</section>
{specials}{items_html}
{visit}{photos}
{rev_html}
</main>
<footer class="foot">
<p><b>{e(name)}</b></p>
<p>{e(" · ".join(x for x in [locs[0]["address"] if locs else "", phone] if x))}</p>
{footer_line(b)}
</footer>
<script>
(function () {{
  try {{
    var d = new Intl.DateTimeFormat("en-US", {{ timeZone: "America/Chicago", weekday: "long" }}).format(new Date());
    var i = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].indexOf(d);
    document.querySelectorAll('.hours tr[data-day="' + i + '"]').forEach(function (r) {{ r.classList.add("today"); }});
  }} catch (err) {{}}
}})();{extra_js}
</script>
</body>
</html>
'''


def sources_txt(b):
    lines = [f"{b['name']} — demo prepared by Lake Houston Web Co, {b['built']}.", "",
             "Facts used on this page and where they came from:"]
    lines += [f"- {s}" for s in b["sources"]]
    if b.get("conflicts"):
        lines += ["", "Conflicts / caveats:"] + [f"- {c}" for c in b["conflicts"]]
    photos = ("Photos on this page were uploaded by the owner through the site editor."
              if b.get("photos") else "No photos are used on this page.")
    lines += ["", photos + " No reviews, hours or prices were invented."]
    return "\n".join(lines) + "\n"


SITES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sites")


def load(args=None):
    """Slugs load _tools/sites/<slug>.json; a path ending in .json loads that file (one business or a list)."""
    files = [a if a.endswith(".json") else os.path.join(SITES, a + ".json") for a in args] if args \
        else sorted(glob.glob(os.path.join(SITES, "*.json")))
    out = []
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        out.extend(d if isinstance(d, list) else [d])
    return out


def main():
    for b in load(sys.argv[2:]):
        d = os.path.join(OUT, b["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(b))
        open(os.path.join(d, "SOURCES.txt"), "w", encoding="utf-8").write(sources_txt(b))
        print("built", b["slug"])


if __name__ == "__main__":
    main()
