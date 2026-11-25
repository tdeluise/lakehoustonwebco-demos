"""Build local search landing pages for lakehoustonwebco.com.
Run from repo root: python3 _tools/seo/build_local.py"""
import json, glob, os, re, collections, datetime, html

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
CSS = re.search(r"<style>(.*?)</style>", home, re.S).group(1)
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&display=swap" rel="stylesheet">'
ICON = re.search(r'<link rel="icon"[^>]*>', home).group(0)
LOGO = re.search(r'<svg viewBox="0 0 64 64".*?</svg>', home, re.S).group(0)
PHONE, TEL, MAIL = "(979) 355-0557", "+19793550557", "lakehoustonwebco@gmail.com"
EXTRA = """
.crumbs{font-size:.9rem;color:var(--ink-soft);margin:8px 0 0}
.crumbs a{color:var(--ink-soft)}
.links{display:flex;flex-wrap:wrap;gap:10px;padding:0;list-style:none}
.links a{display:inline-block;padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--white);text-decoration:none;color:var(--ink)}
.facts{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));padding:0;list-style:none}
.facts li{background:var(--white);border:1px solid var(--line);border-radius:14px;padding:18px}
.facts b{display:block;font-family:var(--display);font-size:1.15rem;margin-bottom:4px}
"""

# count previews built per city (real numbers from the demo specs)
counts = collections.Counter()
for f in glob.glob(os.path.join(ROOT, "_tools/sites/*.json")) + glob.glob(os.path.join(ROOT, "_tools/pro/*.json")):
    try: counts[json.load(open(f)).get("city", "")] += 1
    except Exception: pass

CITIES = [
 # slug, name, county/area note, nearby list, local detail
 ("atascocita","Atascocita","Harris County, on the west shore of Lake Houston",["Humble","Kingwood","Huffman","Crosby"],"FM 1960 and Atascocita Road are lined with owner-run shops, food trucks and service businesses that customers find on their phones first."),
 ("humble","Humble","Harris County, just north of Bush Intercontinental",["Atascocita","Kingwood","Spring","Porter"],"From Main Street to the FM 1960 corridor, Humble has hundreds of well-reviewed local businesses that still send searchers to a Facebook page."),
 ("kingwood","Kingwood","the Livable Forest on the north side of Lake Houston",["Humble","Atascocita","Porter","New Caney"],"Kingwood customers compare options on their phones before they call. A clear page with your hours and a call button wins that moment."),
 ("lake-houston","Lake Houston","the Lake Houston area: Atascocita, Humble, Kingwood, Huffman and Crosby",["Atascocita","Humble","Kingwood","Crosby","Huffman"],"This is home base. Most of the businesses I work with here are owner-run, busy, and great at what they do. They just never had time for a website."),
 ("crosby","Crosby","east Harris County, on the east side of Lake Houston",["Huffman","Atascocita","Baytown"],"Crosby runs on word of mouth. A website makes sure the people hearing about you can actually find your number and hours."),
 ("huffman","Huffman","the northeast shore of Lake Houston",["Crosby","Atascocita","Kingwood"],"Huffman businesses often serve customers from across the lake. A simple site with directions and hours saves them a wasted trip."),
 ("porter","Porter","south Montgomery County along US 59 / I-69",["Kingwood","New Caney","Humble"],"Porter is growing fast, and new residents search online before they pick a mechanic, barber or restaurant."),
 ("new-caney","New Caney","Montgomery County, just north of Kingwood",["Porter","Kingwood","Humble"],"New Caney's local shops compete with chains that all have websites. A real page levels that field for $500."),
 ("spring","Spring","north Harris County along I-45 and FM 1960",["Humble","Houston"],"Spring has a huge number of small service businesses competing for the same searches. Showing up with your own page matters."),
 ("baytown","Baytown","east Harris County on Galveston Bay",["Crosby","Houston"],"Baytown customers search for trades, auto repair and food on their phones. A fast, simple page puts your call button right there."),
 ("houston","Houston","the greater Houston area",["Humble","Spring","Pasadena","Baytown"],"Houston has more small businesses than almost anywhere, and plenty of the best ones still don't have a website."),
 ("bryan","Bryan","Brazos County",["College Station","Navasota"],"Downtown Bryan and the Texas Avenue corridor are full of family businesses with great reviews and no website."),
 ("college-station","College Station","Brazos County, home of Texas A&M",["Bryan","Navasota"],"College Station has a constant flow of new customers every semester, and almost all of them look you up online first."),
 ("navasota","Navasota","Grimes County",["Bryan","College Station"],"Navasota businesses serve locals and people driving through on Highway 6. A website makes you easy to find from the road."),
]
INDUSTRIES = [
 ("restaurants","restaurants","Restaurants","Your menu, hours and a call or order button, right where hungry people are looking.",["Your menu, easy to read on a phone","Today's hours highlighted","Tap to call or get directions","Specials you can update yourself"]),
 ("food-trucks","food trucks","Food trucks","Where you'll be this week, your menu and how to reach you, on one page you can update from your phone.",["This week's locations and times","Your menu and prices","Catering and event contact","Link to your Facebook and Instagram"]),
 ("barbershops","barbershops","Barbershops","Your services, prices, hours and a one-tap call or booking link, so walk-ins and new clients find you first.",["Cuts and prices","Hours and walk-in info","Booking link or call button","Photos of your work"]),
 ("hair-salons","hair and nail salons","Hair and nail salons","A clean page with your services, prices and booking info that looks as good as your work.",["Service menu with prices","Booking or call button","Your hours","Photos of your work"]),
 ("auto-repair","auto repair shops","Auto repair shops","Your services, hours and a big call button, for drivers who need help now.",["What you fix","Hours, including Saturdays","Tap to call or get directions","Your real Google reviews"]),
 ("cleaning-services","cleaning companies","Cleaning companies","A professional page with your services and service area, so homeowners and offices trust you before they call.",["Services and service area","Free estimate call button","Your real reviews","Photos before and after"]),
 ("landscaping","landscaping and lawn care","Landscaping and lawn care","Your services, the neighborhoods you cover and a quick way to ask for a quote.",["Services and seasonal work","Neighborhoods you serve","Call or text for a quote","Photos of finished jobs"]),
 ("contractors","contractors and home services","Contractors and home services","For plumbers, electricians, roofers, painters and handymen: a page that makes you look established and gets the phone ringing.",["Services and licenses","Service area","Call or text button","Photos of your work"]),
]

def page(path, title, desc, h1, lede, body, crumbs, schema_area):
    url = "https://lakehoustonwebco.com/" + path
    schema = {"@context":"https://schema.org","@type":"ProfessionalService","name":"Lake Houston Web Co","url":"https://lakehoustonwebco.com/","telephone":"+1-979-355-0557","email":MAIL,"priceRange":"$500","founder":{"@type":"Person","name":"Todd De Luise"},"areaServed":schema_area,"description":desc}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0d2b2f">
{ICON}
{FONTS}
<script type="application/ld+json">{json.dumps(schema)}</script>
<style>{CSS}{EXTRA}</style>
</head>
<body>
<div class="shell">
<header class="bar">
<a class="mark" href="/" aria-label="Lake Houston Web Co home">{LOGO}Lake Houston Web Co</a>
<a class="bar-link" href="#contact">Get a free preview</a>
</header>
<p class="crumbs">{crumbs}</p>
<main>
<section class="hero" style="grid-template-columns:1fr">
<div>
<h1>{html.escape(h1)}</h1>
<p class="lede">{lede}</p>
<div class="actions">
<a class="btn btn-sun" href="sms:{TEL}">Text Todd for a free preview</a>
<a class="btn btn-plain" href="tel:{TEL}">Call {PHONE}</a>
<a class="btn btn-plain" href="/nice-laser-cleaning/">See a sample site</a>
</div>
</div>
</section>
<section aria-label="Price">
<div class="ticket">
<div class="main"><span class="was"><s>$2,000</s> typical agency price</span><b>$500</b><span>One time, to put your site live</span></div>
<div><b>$0</b><span>Monthly fee</span></div>
<div><b>~$12</b><span>A year for your domain, in your name</span></div>
<div><b>30 days</b><span>Of free text edits after launch</span></div>
</div>
</section>
{body}
<section class="block" id="how">
<h2>How it works</h2>
<ol class="steps">
<li><h3>I build a preview</h3><p>From your public listing: name, hours, address and real reviews. Nothing made up.</p></li>
<li><h3>You look it over</h3><p>I text you the link. Tell me what you'd change.</p></li>
<li><h3>It goes live</h3><p>For $500 I register a domain in your name and put the site on it.</p></li>
<li><h3>Small edits are free</h3><p>New hours or prices in the first 30 days? Just text me.</p></li>
</ol>
</section>
<section class="contact" id="contact">
<div>
<h2>Want to see your free preview?</h2>
<p>Text or email your business name and city. I'll build the preview and send you the link. You don't pay anything unless you want it live.</p>
<p>I'm Todd De Luise, owner of Lake Houston Web Co.</p>
</div>
<div>
<div class="actions">
<a class="btn btn-sun" href="sms:{TEL}">Text Todd</a>
<a class="btn btn-light" href="tel:{TEL}">Call</a>
<a class="btn btn-light" href="mailto:{MAIL}?subject=Free%20preview%20for%20my%20business&amp;body=Business%20name%3A%0ACity%3A%0ABest%20way%20to%20reach%20me%3A%0A">Email</a>
</div>
<p><a class="tel" href="tel:{TEL}">{PHONE}</a></p>
<p><a class="mail" href="mailto:{MAIL}">{MAIL}</a></p>
</div>
</section>
</main>
<footer class="foot">
<span>© 2026 Lake Houston Web Co</span>
<span><a href="/web-design/">Areas we serve</a> · <a href="/websites-for/">Industries</a> · <a href="tel:{TEL}">{PHONE}</a></span>
</footer>
</div>
</body>
</html>
"""

def write(path, content):
    full = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

paths = []
ind_links = "".join(f'<li><a href="/websites-for/{s}/">{T}</a></li>' for s,_,T,_,_ in INDUSTRIES)
city_names = {c[1]: c[0] for c in CITIES}
for slug, name, where, near, detail in CITIES:
    n = counts.get(name, 0) + (sum(counts.get(x,0) for x in ["Atascocita","Humble","Kingwood","Crosby","Huffman"]) if slug=="lake-houston" else 0)
    built = f"<p>I've already built <b>{n} free previews</b> for {name}-area businesses from their public listings.</p>" if n >= 5 else ""
    near_links = "".join(f'<li><a href="/web-design/{city_names[x]}/">{x}</a></li>' for x in near if x in city_names)
    body = f"""<section class="block">
<h2>Websites for {name} small businesses</h2>
<p class="intro">{detail}</p>
{built}
<ul class="facts">
<li><b>Built for phones</b>Call and directions buttons, today's hours highlighted, loads fast on any phone.</li>
<li><b>Yours to keep</b>The domain is registered in your name. No contract and no monthly fee.</li>
<li><b>See it first</b>I build a free preview of your site before you pay anything.</li>
<li><b>Local and reachable</b>Text me directly. No call centers and no tickets.</li>
</ul>
</section>
<section class="block">
<h2>Who I build for in {name}</h2>
<ul class="links">{ind_links}</ul>
<h2 style="margin-top:28px">Nearby areas</h2>
<ul class="links">{near_links}<li><a href="/web-design/">All areas</a></li></ul>
</section>"""
    p = f"web-design/{slug}/"
    write(p, page(p, f"Website Design in {name}, TX | $500, No Monthly Fee | Lake Houston Web Co",
        f"Affordable website design for {name}, TX small businesses. Free preview first, then $500 one time. Domain in your name, no monthly fee. Text Todd at {PHONE}.",
        f"Website design for {name} businesses: $500, no monthly fee",
        f"Serving {where}. I build you a free preview from your public listing. If you like it, it goes live on a domain in your name for $500, one time.",
        body, f'<a href="/">Home</a> › <a href="/web-design/">Areas</a> › {name}', [f"{name}, TX"]))
    paths.append(p)

area_links = "".join(f'<li><a href="/web-design/{s}/">{n}</a></li>' for s,n,_,_,_ in CITIES)
for slug, plural, T, pitch, feats in INDUSTRIES:
    body = f"""<section class="block split">
<div>
<h2>What's on a site for {plural}</h2>
<ul class="checks">{''.join(f'<li><b>{f}</b></li>' for f in feats)}</ul>
</div>
<div>
<h2>Why it matters</h2>
<p class="shops">Most people check a business online before they call or drive over. If all they find is a listing with no website, many pick the next result that has one.</p>
<p class="shops-note">Keep your Facebook and Google listing. Your site links to both and gives searchers one clear page with your phone, hours and address.</p>
</div>
</section>
<section class="block">
<h2>Areas I serve</h2>
<ul class="links">{area_links}</ul>
</section>"""
    p = f"websites-for/{slug}/"
    write(p, page(p, f"Websites for {T} | $500 One Time | Lake Houston Web Co",
        f"Simple, phone-friendly websites for {plural} around Lake Houston, Houston and Bryan–College Station. Free preview, then $500 one time, no monthly fee.",
        f"Websites for {plural}, $500 one time",
        pitch + " Free preview first, then $500 one time with no monthly fee.",
        body, f'<a href="/">Home</a> › <a href="/websites-for/">Industries</a> › {T}', [c[1]+", TX" for c in CITIES]))
    paths.append(p)

# hubs
write("web-design/", page("web-design/", "Website Design Near Lake Houston, Houston & Bryan–College Station | Lake Houston Web Co",
    "Local website design for small businesses in Atascocita, Humble, Kingwood, Houston, Bryan and College Station. $500 one time, no monthly fee.",
    "Local website design, $500 one time", "Pick your area. Every site starts with a free preview built from your public listing.",
    f'<section class="block"><h2>Areas I serve</h2><ul class="links">{area_links}</ul></section>', '<a href="/">Home</a> › Areas', [c[1]+", TX" for c in CITIES]))
write("websites-for/", page("websites-for/", "Websites for Local Businesses by Industry | Lake Houston Web Co",
    "Websites for restaurants, food trucks, barbershops, salons, auto shops, cleaners, landscapers and contractors. $500 one time, no monthly fee.",
    "Websites for local businesses", "Pick your type of business to see what goes on your site.",
    f'<section class="block"><h2>Industries</h2><ul class="links">{ind_links}</ul></section>', '<a href="/">Home</a> › Industries', [c[1]+", TX" for c in CITIES]))
paths += ["web-design/", "websites-for/"]

today = datetime.date.today().isoformat()
urls = [""] + paths
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>https://lakehoustonwebco.com/{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n"
open(os.path.join(ROOT, "sitemap.xml"), "w").write(sm)
print(len(paths), "pages")
