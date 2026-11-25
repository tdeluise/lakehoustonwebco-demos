"""Richer demo pages for the batch 3 and batch 4 slugs.

Category copy is typical for that kind of business. It is not a confirmed
menu, price list, or set of photos. Older demos keep the original renderer.
"""
import csv
import html
import os
import re
from urllib.parse import quote

SKIP = {"blonde-me-hair-salon-pasadena"}
HERE = os.path.dirname(os.path.abspath(__file__))

# phrase fragment -> pack. First match wins, so keep specific phrases first.
RULES = (
    ("school", "generic"),
    ("tattoo", "generic"),
    ("clothing", "generic"),
    ("pet groom", "pet"),
    ("nail", "nails"),
    ("barber", "barber"),
    ("hair salon", "salon"),
    ("lash", "salon"),
    ("wax", "salon"),
    ("tanning", "salon"),
    ("esthetic", "salon"),
    ("beauty", "salon"),
    ("salon", "salon"),
    ("shoe", "shoe"),
    ("tailor", "tailor"),
    ("alteration", "tailor"),
    ("detail", "detail"),
    ("car wash", "detail"),
    ("collision", "body"),
    ("body shop", "body"),
    ("auto body", "body"),
    ("paint and body", "body"),
    ("tire", "tire"),
    ("automotive", "auto"),
    ("auto repair", "auto"),
    ("mechanic", "auto"),
    ("transmission", "auto"),
    ("donut", "bakery"),
    ("bakery", "bakery"),
    ("pastry", "bakery"),
    ("bagel", "bakery"),
    ("cake shop", "bakery"),
    ("patisserie", "bakery"),
    ("snoball", "bakery"),
    ("bbq", "bbq"),
    ("barbecue", "bbq"),
    ("seafood", "seafood"),
    ("crawfish", "seafood"),
    ("burger", "burger"),
    ("taco", "taqueria"),
    ("mexican", "taqueria"),
    ("burrito", "taqueria"),
    ("taqueria", "taqueria"),
    ("food truck", "truck"),
    ("food cart", "truck"),
    ("food trailer", "truck"),
    ("italian ice", "diner"),
    ("sushi", "diner"),
    ("hibachi", "diner"),
    ("banh mi", "diner"),
    ("hot dog", "diner"),
    ("coffee", "diner"),
    ("cafe", "diner"),
    ("bistro", "diner"),
    ("grill", "diner"),
    ("restaurant", "diner"),
    ("cater", "diner"),
    ("snack", "diner"),
    ("food court", "diner"),
)

THEME_PACK = {
    "barber": "barber",
    "salon": "salon",
    "taqueria": "taqueria",
    "diner": "diner",
    "bakery": "bakery",
    "mariscos": "seafood",
    "burger": "burger",
    "rugged": "generic",
}


def _s(title, text):
    return {"title": title, "text": text}


PACKS = {
    "barber": {
        "highlight": "gallery",
        "services": [
            _s("Haircuts", "A standard haircut, cut to the length you ask for."),
            _s("Fades and tapers", "Shorter sides with more length on top."),
            _s("Beard trims", "Trim and shape for a beard or mustache."),
            _s("Line-ups", "A cleaned-up hairline or beard edge."),
            _s("Kids' cuts", "Haircuts for children."),
            _s("Shaves", "A shave is a common barbershop service."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Say what you want", "Name the cut, or describe it in the form."),
            ("Visit the shop", "The listing places the shop in {city}, {state}."),
            ("You are done", "Pay the shop for the service you received."),
        ],
    },
    "salon": {
        "highlight": "gallery",
        "services": [
            _s("Haircuts", "A cut to the length you ask for."),
            _s("Color", "Color service is common at a hair salon. Ask what they offer."),
            _s("Blowouts", "A wash and blow-dry style."),
            _s("Styling", "Styling for an event or a regular visit."),
            _s("Trims", "A shorter visit to take off length."),
            _s("Treatments", "Ask which hair treatments are available."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe your hair", "Say what you want done."),
            ("Visit the salon", "The listing places the salon in {city}, {state}."),
            ("You are done", "Pay the salon for the service you received."),
        ],
    },
    "nails": {
        "highlight": "gallery",
        "services": [
            _s("Manicures", "A manicure on the fingernails."),
            _s("Pedicures", "A pedicure on the toenails."),
            _s("Gel polish", "A longer-wear polish. Ask if they offer it."),
            _s("Nail repair", "Repair for a broken or lifted nail."),
            _s("Polish change", "Remove old polish and apply a new color."),
            _s("Shape and length", "Shaping, and length if you ask for it."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Say what you want", "Name the service, such as a manicure or a pedicure."),
            ("Visit the salon", "The listing places the salon in {city}, {state}."),
            ("You are done", "Pay the salon for the service you received."),
        ],
    },
    "taqueria": {
        "highlight": "menu",
        "services": [
            _s("Tacos", "Tacos are a typical item at this kind of restaurant."),
            _s("Burritos", "A filled burrito is a typical item."),
            _s("Quesadillas", "A quesadilla is a typical item."),
            _s("Tortas", "A torta is a typical sandwich at a Mexican restaurant."),
            _s("Rice and beans", "Rice and beans are a typical side."),
            _s("Drinks", "Ask which drinks are available."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Ask what they have", "The sample list on this page is not their menu."),
            ("Go to the address", "The listing places them in {city}, {state}."),
            ("Order there", "Order and pay at the restaurant."),
        ],
    },
    "diner": {
        "highlight": "menu",
        "services": [
            _s("Plates", "A hot plate is a typical restaurant item."),
            _s("Sandwiches", "Sandwiches are a typical item."),
            _s("Sides", "Sides served with a plate."),
            _s("Drinks", "Ask which drinks are available."),
            _s("Takeout", "Ask if they pack food to go."),
            _s("Catering questions", "Ask if they cater. This page does not confirm that they do."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Ask what they have", "The sample list on this page is not their menu."),
            ("Go to the address", "The listing places them in {city}, {state}."),
            ("Order there", "Order and pay at the restaurant."),
        ],
    },
    "bbq": {
        "highlight": "menu",
        "services": [
            _s("Brisket", "Brisket is a typical barbecue item."),
            _s("Ribs", "Pork or beef ribs are a typical item."),
            _s("Sausage", "Sausage is a typical barbecue item."),
            _s("Chicken", "Chicken is a typical barbecue item."),
            _s("Sides", "Sides served with a plate."),
            _s("Plates", "Meat and sides on one plate. Ask what is offered."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Ask what they have", "The sample list on this page is not their menu."),
            ("Go to the address", "The listing places them in {city}, {state}."),
            ("Order there", "Order and pay at the restaurant."),
        ],
    },
    "bakery": {
        "highlight": "menu",
        "services": [
            _s("Donuts", "Donuts are a typical bakery item. Ask if they make them."),
            _s("Pastries", "Pastries are a typical bakery item."),
            _s("Cakes", "Ask if they take cake orders."),
            _s("Cookies", "Cookies are a typical bakery item."),
            _s("Drinks", "Ask if coffee or other drinks are available."),
            _s("Custom orders", "Ask if they take orders ahead. This page does not confirm that they do."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Ask what they have", "The sample list on this page is not their case."),
            ("Go to the address", "The listing places them in {city}, {state}."),
            ("Buy there", "Pay at the shop for what you take."),
        ],
    },
    "seafood": {
        "highlight": "menu",
        "services": [
            _s("Shrimp", "Shrimp is a typical seafood item."),
            _s("Fish plates", "A fish plate is a typical item."),
            _s("Fried seafood", "Fried seafood is a typical preparation."),
            _s("Grilled seafood", "Grilled seafood is a typical preparation. Ask if they offer it."),
            _s("Sides", "Sides served with a plate."),
            _s("Takeout", "Ask if they pack food to go."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Ask what they have", "The sample list on this page is not their menu."),
            ("Go to the address", "The listing places them in {city}, {state}."),
            ("Order there", "Order and pay at the restaurant."),
        ],
    },
    "burger": {
        "highlight": "menu",
        "services": [
            _s("Burgers", "A burger is the typical main item."),
            _s("Fries", "Fries are a typical side."),
            _s("Sandwiches", "Other sandwiches may be on the board. Ask."),
            _s("Drinks", "Ask which drinks are available."),
            _s("Sides", "Sides besides fries. Ask what they have."),
            _s("Takeout", "Ask if they pack food to go."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Ask what they have", "The sample list on this page is not their menu."),
            ("Go to the address", "The listing places them in {city}, {state}."),
            ("Order there", "Order and pay at the restaurant."),
        ],
    },
    "truck": {
        "highlight": "menu",
        "services": [
            _s("Plates", "A plate from the truck is a typical order."),
            _s("Handhelds", "Tacos, sandwiches, or similar handhelds. Ask what they serve."),
            _s("Sides", "A side with the main item."),
            _s("Drinks", "Ask which drinks are available."),
            _s("Window service", "Order at the truck window."),
            _s("Today's food", "Ask what they are cooking. This page does not list it."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Ask what they have", "The sample list on this page is not their menu."),
            ("Go to the listed spot", "The listing places them in {city}, {state}."),
            ("Order at the truck", "Order and pay at the window."),
        ],
    },
    "auto": {
        "highlight": "illustration",
        "services": [
            _s("Oil changes", "An oil change is a typical shop service."),
            _s("Brake service", "Brake work is a typical shop service."),
            _s("Diagnostics", "A check to see why a vehicle is acting up."),
            _s("Batteries", "Battery test or replacement. Ask the shop."),
            _s("Belts and hoses", "Common wear parts a shop can inspect."),
            _s("Your symptom", "Describe the noise, leak, or warning light and ask."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe the vehicle", "Say what it is doing, not what you think the part is."),
            ("Go to the shop", "The listing places the shop in {city}, {state}."),
            ("Ask before work starts", "Confirm the work with the shop before they begin."),
        ],
    },
    "body": {
        "highlight": "slider",
        "services": [
            _s("Dent repair", "Body work on a dent. Ask what they take on."),
            _s("Panel work", "Repair or replacement of a body panel."),
            _s("Paint questions", "Ask about paint for a repaired panel."),
            _s("Bumper repair", "Bumper scuffs and cracks. Ask the shop."),
            _s("Collision questions", "Ask whether they handle insurance jobs."),
            _s("In-person look", "A body shop usually needs to see the vehicle."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe the damage", "Say what was hit. Photos in the form can help."),
            ("Go to the shop", "The listing places the shop in {city}, {state}."),
            ("Review the plan", "The shop explains the work before it starts."),
        ],
    },
    "tire": {
        "highlight": "illustration",
        "services": [
            _s("Flat repair", "Repair of a puncture, when the tire can be repaired."),
            _s("Tire replacement", "A new tire. Ask which sizes they stock."),
            _s("Balance", "Balancing a tire on the wheel."),
            _s("Rotation", "Moving tires to even out wear."),
            _s("Pressure check", "A check of the air pressure."),
            _s("Your size", "The size is on the tire sidewall. Bring it when you ask."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Read the sidewall", "The tire size is printed on the tire."),
            ("Go to the shop", "The listing places the shop in {city}, {state}."),
            ("Drive out", "Pay the shop for the work they did."),
        ],
    },
    "detail": {
        "highlight": "slider",
        "services": [
            _s("Exterior wash", "A wash of the outside of the vehicle."),
            _s("Interior clean", "Vacuum and a wipe-down inside."),
            _s("Wheels", "Cleaning the wheels and tires."),
            _s("Wax or sealant", "A protective coat. Ask if they offer it."),
            _s("Stain questions", "Ask about a specific stain before you book."),
            _s("The vehicle", "Tell them the vehicle type so they know the job size."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe the vehicle", "Say what you want cleaned."),
            ("Go to the shop", "The listing places them in {city}, {state}."),
            ("Pick it up", "Pay them for the work they did."),
        ],
    },
    "pet": {
        "highlight": "illustration",
        "services": [
            _s("Bath", "A wash for the coat."),
            _s("Haircut", "A cut to the length you ask for."),
            _s("Brush-out", "Brushing out the coat."),
            _s("Nail trim", "Trimming the nails."),
            _s("Ears", "Ask if ear cleaning is part of the visit."),
            _s("Coat type", "Tell them the breed or coat so they know the job."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe the pet", "Name the breed or coat and the service you want."),
            ("Go to the shop", "The listing places them in {city}, {state}."),
            ("Pick up", "Pay them for the service they did."),
        ],
    },
    "tailor": {
        "highlight": "illustration",
        "services": [
            _s("Hems", "Shortening or lengthening a hem."),
            _s("Take in or let out", "Making a garment smaller or larger."),
            _s("Zippers", "Replacing a zipper."),
            _s("Buttons", "Replacing a button."),
            _s("Simple repairs", "A seam or a small tear. Ask if they can do it."),
            _s("The garment", "Bring the item, or describe it in the form."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe the garment", "Say what needs to change."),
            ("Bring it in", "The listing places them in {city}, {state}."),
            ("Pick it up", "Pay them for the alteration they did."),
        ],
    },
    "shoe": {
        "highlight": "illustration",
        "services": [
            _s("Heel repair", "Rebuilding or replacing a heel."),
            _s("Sole repair", "Repairing a worn sole."),
            _s("Stitching", "Restitching a seam that has opened."),
            _s("Polish", "A shine and polish."),
            _s("Stretching", "Stretching a tight spot. Ask if they do it."),
            _s("The pair", "Bring the shoes so they can see the repair."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe the pair", "Say what is worn or broken."),
            ("Bring them in", "The listing places the shop in {city}, {state}."),
            ("Pick them up", "Pay the shop for the repair they did."),
        ],
    },
    "generic": {
        "highlight": "illustration",
        "services": [
            _s("What they offer", "Ask which services are available. This page does not have a confirmed list."),
            _s("The job", "Describe what you need done."),
            _s("Timing", "Ask when they can see you. Hours are not listed here."),
            _s("A visit", "Ask whether you go to them in {city}."),
            _s("What to bring", "Ask what you should have with you."),
            _s("A follow-up", "Call or use the form if you need to write again."),
        ],
        "steps": [
            ("Reach out", "Call or use the form on this page."),
            ("Describe the job", "Say what you need. Do not assume a service list."),
            ("Ask about a visit", "The listing places them in {city}, {state}."),
            ("Confirm with them", "They tell you the next step."),
        ],
    },
}


def e(s):
    return html.escape(str(s), quote=True)


def tel(p):
    d = "".join(ch for ch in p if ch.isdigit())
    return "+1" + d if len(d) == 10 else ("+" + d if d else "")


def maps(addr):
    return "https://www.google.com/maps/search/?api=1&query=" + quote(addr)


def article(phrase):
    word = phrase.split()[0].lower() if phrase else "local"
    if word.startswith(("use", "uni")):
        return "a"
    if word[:1] in "aeiou":
        return "an"
    return "a"


def place_parts(b):
    city = (b.get("city") or "").strip()
    st = (b.get("st") or "TX").strip()
    eye = (b.get("eyebrow") or "").strip()
    phrase = eye.split("·", 1)[0].strip() if "·" in eye else ""
    state_name = st
    if "·" in eye and "," in eye.split("·", 1)[1]:
        state_name = eye.split("·", 1)[1].split(",", 1)[1].strip() or st
    if not phrase:
        phrase = {"barber": "Barbershop", "salon": "Salon", "taqueria": "Mexican restaurant",
                  "diner": "Restaurant", "bakery": "Bakery", "mariscos": "Seafood restaurant",
                  "burger": "Burger restaurant", "rugged": "Local business"}.get(b.get("theme"), "Local business")
    return phrase, city, st, state_name


def pack_key(phrase, theme):
    low = phrase.lower()
    for needle, key in RULES:
        if needle in low:
            return key
    return THEME_PACK.get(theme, "generic")


def source_label(b):
    text = " ".join(b.get("sources") or [])
    m = re.search(r"https?://(?:www\.)?([^/\s]+)", text)
    host = m.group(1) if m else "the public listing"
    when = (b.get("built") or "").strip() or "the listing date"
    return host, when


def rich_slug_set():
    found = set()
    for name in ("batch3-live.csv", "batch4-live.csv"):
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            continue
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                slug = (row.get("slug") or "").strip()
                if slug:
                    found.add(slug)
    return found - SKIP


_RICH = None


def uses_rich(slug):
    global _RICH
    if _RICH is None:
        _RICH = rich_slug_set()
    return slug in _RICH


def icons(accent):
    paths = (
        "M4 20h16M6 20V10h12v10M9 20v-4h6v4M4 10l8-6 8 6",
        "M4 7h16v12H4zM4 7l8 6 8-6",
        "M12 3v18M5 8h14M5 16h14",
        "M5 19l4-8 3 5 3-7 4 10",
        "M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z",
        "M4 12h16M12 4v16",
    )
    out = []
    for d in paths:
        out.append(
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        )
    return out


def hero_visual(kind, phrase):
    label = e(phrase)
    if kind == "slider":
        inner = '<div class="split"><span>Before</span><span>After</span></div>'
    elif kind == "menu":
        inner = '<div class="plate" aria-hidden="true"></div><p>Sample menu</p>'
    elif kind == "gallery":
        inner = '<div class="swatches" aria-hidden="true"><i></i><i></i><i></i><i></i></div><p>Style ideas</p>'
    else:
        inner = f'<div class="mark" aria-hidden="true"></div><p>{label}</p>'
    return f'<div class="visual" aria-hidden="true">{inner}<small>Illustration</small></div>'


def highlight_html(kind, pack, phrase, accent):
    note = "Illustration only. Not a photo or a confirmed list from this business."
    if kind == "slider":
        body = f'''<div class="ba" id="ba">
<div class="layer after"></div>
<div class="layer before"></div>
<span class="lbl b">Before</span><span class="lbl a">After</span>
<div class="handle"></div>
<input type="range" min="0" max="100" value="58" aria-label="Illustration before and after slider" id="baRange">
</div>
<p class="fine">{e(note)}</p>'''
        title = "Before and after"
        lead = "Drag the slider. This is a drawing of a typical result, not a job from this business."
    elif kind == "menu":
        rows = []
        for item in pack["services"]:
            rows.append(f'<li><strong>{e(item["title"])}</strong><span>{e(item["text"])}</span></li>')
        body = f'<ul class="menu">{"".join(rows)}</ul><p class="fine">Sample menu. {e(note)}</p>'
        title = "Sample menu"
        lead = f'Typical items for {article(phrase)} {phrase.lower()}. Not this business\'s menu, and no prices are shown.'
    elif kind == "gallery":
        tiles = "".join(f'<figure><span class="tile t{i}"></span><figcaption>{e(n)}</figcaption></figure>'
                        for i, n in enumerate(("Cut", "Finish", "Shape", "Detail")))
        body = f'<div class="gallery">{tiles}</div><p class="fine">Style gallery placeholder. {e(note)}</p>'
        title = "Style gallery"
        lead = "Drawn style tiles, not photos from this shop."
    else:
        body = f'<div class="illus"><p>{e(phrase)}</p><small>Illustration</small></div><p class="fine">{e(note)}</p>'
        title = "A look at the work"
        lead = "A drawing for this kind of business. Not a photo from them."
    return f'''<section class="band" id="highlight"><div class="wrap">
<p class="eyebrow">Highlight</p>
<h2>{e(title)}</h2>
<p class="lead">{lead}</p>
{body}
</div></section>'''


def page_rich(b):
    from build_demos import THEMES
    theme = THEMES.get(b.get("theme") or "diner", THEMES["diner"])
    phrase, city, st, state_name = place_parts(b)
    key = pack_key(phrase, b.get("theme"))
    pack = PACKS[key]
    name = b.get("name") or "This business"
    phone = (b.get("phone") or "").strip()
    fb = (b.get("facebook") or "").strip()
    addr = (b.get("address") or "").strip()
    rating = b.get("rating") or {}
    about = b.get("about") or []
    if not about:
        about = [f"{name} is {article(phrase)} {phrase.lower()} in {city}, {state_name}."]
    host, when = source_label(b)
    icos = icons(theme["accent"])
    kind = pack["highlight"]

    chips = []
    if rating.get("value"):
        chips.append(f'{e(rating["value"])} stars on Google')
    if rating.get("count"):
        word = "review" if str(rating["count"]) == "1" else "reviews"
        chips.append(f'{e(rating["count"])} Google {word}')
    if city:
        chips.append(f'{e(city)}, {e(state_name)}')
    chip_html = "".join(f'<li>{c}</li>' for c in chips)

    stats = []
    if rating.get("value"):
        stats.append((str(rating["value"]), "stars on Google"))
    if rating.get("count"):
        word = "Google review" if str(rating["count"]) == "1" else "Google reviews"
        stats.append((str(rating["count"]), word))
    if city:
        stats.append((city, f"City served · {state_name}"))
    stat_html = "".join(f'<article class="stat"><b>{e(val)}</b><span>{e(label)}</span></article>' for val, label in stats)

    cards = []
    for i, item in enumerate(pack["services"]):
        text = item["text"].replace("{city}", city).replace("{state}", state_name)
        cards.append(
            f'<article class="card"><div class="ico">{icos[i % len(icos)]}</div><h3>{e(item["title"])}</h3><p>{e(text)}</p></article>'
        )
    options = "".join(f'<option>{e(item["title"])}</option>' for item in pack["services"])
    steps = []
    for i, (title, text) in enumerate(pack["steps"], 1):
        text = text.replace("{city}", city).replace("{state}", state_name)
        steps.append(f'<li><span>{i}</span><h3>{e(title)}</h3><p>{e(text)}</p></li>')

    if phone:
        nav_cta = f'<a class="btn solid" href="tel:{tel(phone)}">Call</a>'
        hero_primary = f'<a class="btn solid" href="tel:{tel(phone)}">Call {e(phone)}</a>'
        hero_second = '<a class="btn line" href="#contact">Get a Quote</a>'
    else:
        nav_cta = '<a class="btn solid" href="#contact">Get a Quote</a>'
        hero_primary = '<a class="btn solid" href="#contact">Get a Quote</a>'
        if addr:
            hero_second = f'<a class="btn line" href="{e(maps(addr))}" target="_blank" rel="noopener">Directions</a>'
        elif fb:
            hero_second = f'<a class="btn line" href="{e(fb)}" target="_blank" rel="noopener">Facebook</a>'
        else:
            hero_second = '<a class="btn line" href="#services">Services</a>'

    contact_bits = []
    if phone:
        contact_bits.append(f'<a class="row" href="tel:{tel(phone)}"><b>Call</b><span>{e(phone)}</span></a>')
    if fb:
        contact_bits.append(f'<a class="row" href="{e(fb)}" target="_blank" rel="noopener"><b>Facebook</b><span>Page listed for this business</span></a>')
    if addr:
        contact_bits.append(f'<a class="row" href="{e(maps(addr))}" target="_blank" rel="noopener"><b>Address</b><span>{e(addr)}</span></a>')
    elif city:
        contact_bits.append(f'<p class="row"><b>City</b><span>{e(city)}, {e(state_name)}</span></p>')

    about_html = "".join(f"<p>{e(p)}</p>" for p in about)
    note = f"Services shown are typical for {article(phrase)} {phrase.lower()}; the owner can edit them."
    robots = "" if b.get("launched") else '<meta name="robots" content="noindex, nofollow">'
    desc = b.get("tagline") or about[0]

    css = """
:root {{ --bg:{bg}; --card:{surface}; --ink:{ink}; --muted:{muted}; --accent:{accent}; --accent2:{accent2}; --band:{band}; --bandink:{bandink}; --display:{display}; --body:{body}; }}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 var(--body); }}
a {{ color:inherit; }}
img,svg {{ display:block; max-width:100%; }}
.wrap {{ width:min(1100px, calc(100% - 32px)); margin:0 auto; }}
h1,h2,h3 {{ font-family:var(--display); line-height:1.05; margin:0 0 .4rem; text-wrap:balance; }}
.ribbon {{ background:var(--band); color:var(--bandink); text-align:center; font-size:.82rem; font-weight:700; padding:8px 14px; }}
.nav {{ position:sticky; top:0; z-index:20; background:color-mix(in srgb, var(--band) 92%, transparent); color:var(--bandink); backdrop-filter:blur(12px); }}
.nav .in {{ display:flex; align-items:center; justify-content:space-between; gap:12px; min-height:64px; }}
.brand {{ color:var(--bandink); text-decoration:none; font-family:var(--display); font-size:1.15rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:46vw; }}
.links {{ display:none; }}
.links a {{ color:var(--bandink); text-decoration:none; font-weight:650; }}
.btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:46px; padding:10px 16px; border-radius:999px; font-weight:750; text-decoration:none; border:0; cursor:pointer; font:inherit; }}
.solid {{ background:var(--accent); color:#fff; }}
.line {{ background:transparent; color:var(--ink); border:2px solid var(--ink); }}
.nav .solid {{ color:#fff; }}
.burger {{ background:none; border:0; color:var(--bandink); font-size:1.6rem; cursor:pointer; }}
.hero {{ padding:36px 0 28px; }}
.hero-grid {{ display:grid; gap:22px; }}
.eyebrow {{ letter-spacing:.14em; text-transform:uppercase; font-size:.75rem; font-weight:750; color:var(--accent2); margin:0 0 10px; }}
h1 {{ font-size:clamp(2.3rem, 10vw, 4.6rem); }}
.about p {{ font-size:1.05rem; max-width:62ch; }}
.ctas,.trust {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }}
.trust {{ list-style:none; padding:0; }}
.trust li {{ background:var(--card); border-radius:999px; padding:7px 12px; font-weight:700; font-size:.9rem; }}
.visual {{ background:var(--card); border-radius:22px; min-height:220px; display:grid; place-items:center; text-align:center; padding:18px; position:relative; }}
.visual p,.visual small {{ margin:8px 0 0; font-weight:750; }}
.visual small {{ color:var(--muted); font-weight:650; }}
.plate {{ width:140px; height:140px; border-radius:50%; background:radial-gradient(circle at 40% 40%, #fff, var(--accent2) 42%, var(--accent) 70%); }}
.swatches,.split {{ display:flex; gap:8px; }}
.swatches i,.split span {{ width:54px; height:72px; border-radius:10px; display:block; }}
.swatches i:nth-child(1) {{ background:var(--accent); }}
.swatches i:nth-child(2) {{ background:var(--accent2); }}
.swatches i:nth-child(3) {{ background:var(--band); }}
.swatches i:nth-child(4) {{ background:var(--ink); }}
.split {{ width:100%; }}
.split span {{ flex:1; height:140px; display:grid; place-items:center; color:#fff; font-weight:750; }}
.split span:first-child {{ background:#8a8175; }}
.split span:last-child {{ background:var(--accent); }}
.mark {{ width:120px; height:120px; border-radius:28px; background:linear-gradient(145deg, var(--accent), var(--accent2)); }}
section {{ padding:42px 0; }}
.band {{ background:color-mix(in srgb, var(--ink) 5%, var(--bg)); }}
h2 {{ font-size:clamp(1.8rem, 5vw, 2.7rem); }}
.lead {{ color:var(--muted); max-width:62ch; }}
.grid {{ display:grid; gap:12px; }}
.card {{ background:var(--card); border-radius:16px; padding:16px; }}
.card h3 {{ font-size:1.15rem; }}
.card p,.fine,.step p,.menu span {{ color:var(--muted); margin:0; }}
.ico svg {{ width:28px; height:28px; }}
.note {{ color:var(--muted); font-size:.9rem; margin-top:14px; }}
.ba {{ position:relative; aspect-ratio:16/10; border-radius:18px; overflow:hidden; background:#d9d3c8; }}
.ba .layer {{ position:absolute; inset:0; }}
.ba .after {{ background:linear-gradient(160deg, #f4f1ea, var(--accent2)); }}
.ba .before {{ background:repeating-linear-gradient(135deg,#6f675c 0 12px,#4e4840 12px 24px); clip-path:inset(0 calc(100% - var(--pos,58%)) 0 0); }}
.ba .lbl {{ position:absolute; top:12px; background:rgba(0,0,0,.65); color:#fff; border-radius:999px; padding:4px 10px; font-size:.78rem; font-weight:750; }}
.ba .lbl.b {{ left:12px; }} .ba .lbl.a {{ right:12px; }}
.ba .handle {{ position:absolute; top:0; bottom:0; left:var(--pos,58%); width:3px; background:#fff; transform:translateX(-50%); }}
.ba input {{ position:absolute; inset:0; width:100%; opacity:0; cursor:ew-resize; margin:0; }}
.menu {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; }}
.menu li {{ background:var(--card); border-radius:14px; padding:14px 16px; display:flex; justify-content:space-between; gap:12px; }}
.gallery {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
.gallery figure {{ margin:0; background:var(--card); border-radius:14px; overflow:hidden; }}
.tile {{ display:block; height:110px; }}
.t0 {{ background:linear-gradient(160deg, var(--accent), var(--ink)); }}
.t1 {{ background:linear-gradient(160deg, var(--accent2), var(--accent)); }}
.t2 {{ background:linear-gradient(160deg, var(--band), var(--accent2)); }}
.t3 {{ background:repeating-linear-gradient(90deg, var(--accent) 0 14px, var(--card) 14px 22px); }}
.gallery figcaption {{ padding:8px 10px; font-weight:750; }}
.illus {{ min-height:200px; border-radius:18px; display:grid; place-items:center; text-align:center; background:linear-gradient(160deg, var(--card), var(--accent2)); padding:20px; }}
.illus p {{ font-family:var(--display); font-size:clamp(1.8rem, 5vw, 3rem); margin:0; }}
.stats {{ display:grid; gap:12px; }}
.stat {{ background:var(--card); border-radius:16px; padding:16px; }}
.stat b {{ display:block; font-family:var(--display); font-size:clamp(1.8rem, 6vw, 2.8rem); color:var(--accent); line-height:1; }}
.steps {{ list-style:none; padding:0; margin:0; display:grid; gap:12px; }}
.steps li {{ background:var(--card); border-radius:16px; padding:16px; }}
.steps span {{ display:inline-grid; place-items:center; width:32px; height:32px; border-radius:50%; background:var(--accent); color:#fff; font-weight:800; }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }}
.chips span,.addr {{ background:var(--card); border-radius:999px; padding:8px 12px; font-weight:750; }}
.addr {{ display:inline-block; border-radius:14px; }}
.contact {{ display:grid; gap:16px; }}
.rows {{ display:grid; gap:8px; }}
.row {{ display:flex; justify-content:space-between; gap:12px; background:var(--card); border-radius:14px; padding:12px 14px; text-decoration:none; }}
form {{ display:grid; gap:10px; background:var(--card); border-radius:18px; padding:16px; }}
label {{ display:grid; gap:4px; font-weight:700; font-size:.9rem; }}
input,select,textarea {{ font:inherit; color:var(--ink); background:var(--bg); border:1px solid color-mix(in srgb, var(--ink) 20%, transparent); border-radius:10px; padding:12px; width:100%; }}
.thanks {{ display:none; font-weight:750; }}
footer {{ background:var(--band); color:var(--bandink); padding:28px 0 36px; }}
footer p {{ margin:0; }}
@media (min-width:760px) {{
  .grid,.stats,.steps,.menu {{ grid-template-columns:1fr 1fr; }}
  .gallery {{ grid-template-columns:repeat(4, 1fr); }}
  .hero-grid,.contact {{ grid-template-columns:1.1fr .9fr; align-items:center; }}
}}
@media (min-width:980px) {{
  .links {{ display:flex; gap:16px; align-items:center; }}
  .burger {{ display:none; }}
  .grid,.stats,.steps {{ grid-template-columns:repeat(3, 1fr); }}
  .steps {{ grid-template-columns:repeat(4, 1fr); }}
  .links.open {{ display:flex; }}
}}
@media (max-width:979px) {{
  .links.open {{ display:flex; flex-direction:column; position:absolute; left:0; right:0; top:64px; background:var(--band); padding:8px 16px 16px; }}
  .links.open a {{ padding:10px 0; }}
}}
@media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} }}
""".format(
        bg=theme["bg"], surface=theme["surface"], ink=theme["ink"], muted=theme["muted"],
        accent=theme["accent"], accent2=theme["accent2"], band=theme["band"], bandink=theme["band_ink"],
        display=theme["display"], body=theme["body"],
    )

    head = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
{robots}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} — {e(city)}, {e(st)}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{theme["fonts"]}&display=swap" rel="stylesheet">
<style>'''
    tail = f'''</style>
</head>
<body>
<p class="ribbon">Demo preview. Not an official site.</p>
<header class="nav"><div class="wrap in">
<a class="brand" href="#top">{e(b.get("short") or name)}</a>
<nav class="links" id="navLinks">
<a href="#services">Services</a>
<a href="#highlight">Highlight</a>
<a href="#why">Why us</a>
<a href="#process">How it works</a>
<a href="#area">Area</a>
<a href="#contact">Contact</a>
</nav>
{nav_cta}
<button class="burger" id="burger" type="button" aria-label="Menu">Menu</button>
</div></header>
<main>
<section class="hero" id="top"><div class="wrap hero-grid">
<div>
<p class="eyebrow">{e(phrase)} · {e(city)}, {e(state_name)}</p>
<h1>{e(name)}</h1>
<div class="about">{about_html}</div>
<div class="ctas">{hero_primary}{hero_second}</div>
<ul class="trust">{chip_html}</ul>
</div>
{hero_visual(kind, phrase)}
</div></section>
<section id="services"><div class="wrap">
<p class="eyebrow">Services</p>
<h2>Typical {e(phrase.lower())} services</h2>
<p class="lead">These cards describe the category. They are not a confirmed list from {e(name)}.</p>
<div class="grid">{"".join(cards)}</div>
<p class="note">{e(note)}</p>
</div></section>
{highlight_html(kind, pack, phrase, theme["accent"])}
<section id="why"><div class="wrap">
<p class="eyebrow">From the listing</p>
<h2>Numbers we can actually show</h2>
<p class="lead">Only figures that were on the public listing, plus the city.</p>
<div class="stats">{stat_html}</div>
</div></section>
<section class="band" id="process"><div class="wrap">
<p class="eyebrow">How it works</p>
<h2>Four steps</h2>
<ol class="steps">{"".join(steps)}</ol>
</div></section>
<section id="area"><div class="wrap">
<p class="eyebrow">Area served</p>
<h2>{e(city)}, {e(state_name)}</h2>
<p class="lead">The listing names this city and state. Nearby areas are not listed here.</p>
<p><span class="addr">{e(addr or (city + ", " + st))}</span></p>
<div class="chips"><span>{e(city)}</span><span>{e(state_name)}</span></div>
</div></section>
<section class="band" id="contact"><div class="wrap contact">
<div>
<p class="eyebrow">Contact</p>
<h2>Call or send a note</h2>
<p class="lead">The form is a demo. Nothing is sent.</p>
<div class="rows">{"".join(contact_bits)}</div>
</div>
<form id="quote">
<label>Name<input name="name" autocomplete="name"></label>
<label>Phone<input name="phone" type="tel" autocomplete="tel"></label>
<label>Email<input name="email" type="email" autocomplete="email"></label>
<label>Service<select name="service">{options}</select></label>
<label>Note<textarea name="note" rows="4"></textarea></label>
<button class="btn solid" type="submit">Get a Quote</button>
<p class="thanks" id="thanks">Demo form: nothing was sent</p>
</form>
</div></section>
</main>
<footer><div class="wrap"><p>Demo site prepared by Lake Houston Web Co. Not an official site. Facts from {e(host)} as of {e(when)}.</p></div></footer>
<script>
document.getElementById("burger").onclick=function(){{document.getElementById("navLinks").classList.toggle("open");}};
document.querySelectorAll("#navLinks a").forEach(function(a){{a.onclick=function(){{document.getElementById("navLinks").classList.remove("open");}};}});
var range=document.getElementById("baRange");
if(range){{range.addEventListener("input",function(){{document.getElementById("ba").style.setProperty("--pos",range.value+"%");}});}}
document.getElementById("quote").addEventListener("submit",function(ev){{ev.preventDefault();ev.currentTarget.querySelectorAll("label,button").forEach(function(n){{n.style.display="none";}});document.getElementById("thanks").style.display="block";}});
</script>
</body>
</html>
'''
    return head + css + tail
