"""'Online today vs. this site' comparison section for demo pages.

Used by build_demos.py (data-driven demos). The section only states what we
found (a Facebook page or listings, no working website) and what the demo adds.
Never shown on launched client sites.
"""
import html
import re
import unicodedata


def e(s):
    return html.escape(str(s), quote=True)


def _slug(s):
    """Example domain stem: the name's words, stopping once it gets long (keeps it readable)."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    words = re.sub(r"[^a-z0-9 ]+", "", s.lower().replace("&", " and ").replace("'", "")).split()
    out = ""
    for w in words:
        if out and len(out) + len(w) > 22:
            break
        out += w
    return out


OK = '<span class="ol-yes" aria-label="Yes">&#10003;</span>'
NO = '<span class="ol-no" aria-label="No">&#10005;</span>'

# Colors come from --ol-* custom properties, set by each template.
CSS = """
.ol{padding:46px 18px;background:var(--ol-bg)}
.ol-in{width:min(1040px,100%);margin:0 auto}
.ol-eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:.78rem;font-weight:700;color:var(--ol-accent);margin:0 0 10px}
.ol h2{font-size:clamp(1.8rem,5vw,2.6rem);margin:0 0 .6rem}
.ol-sub{color:var(--ol-muted);max-width:62ch;margin:0 0 26px;font-size:1.05rem}
.ol-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:22px}
.ol-grid>*{min-width:0}
.ol-card{border-radius:16px;padding:24px;background:var(--ol-card);border:1px solid var(--ol-line)}
.ol-today{border-style:dashed;background:transparent}
.ol-next{border:2px solid var(--ol-accent)}
.ol-tag{display:inline-block;font-size:.7rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;padding:4px 11px;border-radius:999px;background:var(--ol-line);color:var(--ol-ink);margin-bottom:10px}
.ol-next .ol-tag{background:var(--ol-accent);color:#fff}
.ol-card h3{font-size:1.35rem;margin:0 0 14px}
.ol-card ul{list-style:none;margin:0;padding:0;display:grid;gap:13px}
.ol-card li{display:flex;gap:11px;align-items:flex-start}
.ol-card li b{display:block}
.ol-card li small{display:block;color:var(--ol-muted);font-size:.9rem;line-height:1.45;overflow-wrap:anywhere}
.ol-yes,.ol-no{flex:none;width:24px;height:24px;border-radius:50%;display:inline-grid;place-items:center;font-weight:800;font-size:.8rem;line-height:1}
.ol-yes{background:color-mix(in srgb,var(--ol-accent) 16%,transparent);color:var(--ol-accent)}
.ol-no{background:rgba(214,69,69,.14);color:#c43c3c}
.ol-part{color:var(--ol-muted);font-size:.82rem;font-weight:600}
.ol-scroll{border-radius:14px;border:1px solid var(--ol-line);overflow:hidden}
.ol-table{width:100%;border-collapse:collapse;background:var(--ol-card)}
.ol-table th,.ol-table td{padding:12px 14px;text-align:left;border-bottom:1px solid var(--ol-line);font-size:.95rem}
.ol-table th{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ol-muted)}
.ol-table td:nth-child(n+2),.ol-table th:nth-child(n+2){text-align:center;width:24%}
.ol-table td .ol-yes,.ol-table td .ol-no{margin:0 auto}
.ol-table tr:last-child td{border-bottom:0}
.ol-table .sm{display:none}
.ol-note{color:var(--ol-muted);font-size:.9rem;margin:14px 0 0}
@media (max-width:700px){.ol-grid{grid-template-columns:1fr}}
@media (max-width:560px){.ol-table th,.ol-table td{padding:10px 7px;font-size:.84rem}.ol-table .lg{display:none}.ol-table .sm{display:inline}
.ol-table td:nth-child(n+2),.ol-table th:nth-child(n+2){width:22%}.ol-part{font-size:.72rem}.ol-card{padding:20px 18px}}
"""


def section(short, city, kind, has_fb, noun="Menu", editor=False, domain=None):
    """kind: e.g. 'taqueria' (searched as '<kind> in <city>'). noun: 'Menu' or 'Services'."""
    domain = domain or (_slug(short) + ".com")
    spread = "Spread across Facebook and listing sites" if has_fb else "Spread across listing sites"
    today = [(OK, "Facebook page", "Posts, photos and contact details") if has_fb
             else (OK, "Listings on other sites", "Directory and review sites with the basics"),
             (NO, "No working website found", f"When we looked {short} up, we couldn't find a working site of its own."),
             (NO, f"{noun}, hours and directions in one place", spread)]
    site = [(OK, "Your own web address", f"Something like {domain} (example), for cards, signs and your truck"),
            (OK, "A real site in Google results", f"Built for people who search \u201c{kind} in {city}\u201d"),
            (OK, f"{noun}, hours and directions together", "One page that works on any phone, no login needed"),
            (OK, "Tap to call, tap for directions", "Big buttons right at the top of the page")]
    if editor:
        site.append((OK, "Updates from your phone", "Change your hours, specials and photos yourself"))
    li = lambda rows: "".join(f"<li>{m}<div><b>{e(t)}</b><small>{e(d)}</small></div></li>" for m, t, d in rows)
    part = lambda t: f'<span class="ol-part">{e(t)}</span>'
    rows = [("Your own web address", NO, OK), ("Your own site in Google results", NO, OK)]
    if has_fb:
        rows += [("Easy to view without logging in to Facebook", part("Login pop-ups"), OK),
                 ("No ads or other businesses' pages next to yours", NO, OK)]
    rows.append((f"{noun}, hours and directions on one page", part("Spread out"), OK))
    trs = "".join(f"<tr><td>{e(r)}</td><td>{a}</td><td>{c}</td></tr>" for r, a, c in rows)
    left = "Facebook page only" if has_fb else "Listings only"
    left_sm = "Facebook only" if has_fb else "Listings"
    right = "Facebook + this website" if has_fb else "With this website"
    note = ('<p class="ol-note">Keep the Facebook page for posts and reviews. A website works alongside it.</p>' if has_fb
            else '<p class="ol-note">Your listings still help people find you. A website gives them somewhere to land.</p>')
    return f'''<section class="ol" id="online"><div class="ol-in">
<p class="ol-eyebrow">For {e(short)}: online today vs. this site</p>
<h2>Where you stand online, and what this site adds.</h2>
<p class="ol-sub">What we found when we looked {e(short)} up, next to what this website gives you.</p>
<div class="ol-grid"><div class="ol-card ol-today"><span class="ol-tag">Today</span><h3>{"Facebook and listings" if has_fb else "Listings only"}</h3><ul>{li(today)}</ul></div>
<div class="ol-card ol-next"><span class="ol-tag">With this website</span><h3>A home base online</h3><ul>{li(site)}</ul></div></div>
<div class="ol-scroll"><table class="ol-table"><thead><tr><th>Side by side</th><th><span class="lg">{left}</span><span class="sm">{left_sm}</span></th><th><span class="lg">{right}</span><span class="sm">+ Website</span></th></tr></thead><tbody>{trs}</tbody></table></div>
{note}
</div></section>'''
