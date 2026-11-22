"""Lake Houston Web Co "pro" demo generator.

Builds a full custom-feeling one-page site per business (hero visual, services,
an interactive section that fits the trade, about, area, process, quote form),
modelled on nice-laser-cleaning/. Facts come only from the business's own public
pages; generic copy describes the trade, never invents reviews, prices or awards.

Usage: python3 _tools/build_pro.py <output_root> [slug ...]   (no slugs = build all)
Data:  _tools/pro/<slug>.json, one business per file.
"""
import glob
import hashlib
import html
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "pro")


def e(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and").replace("'", ""))).strip("-")


def hl(s):
    """*word* -> highlighted span."""
    return re.sub(r"\*(.+?)\*", r'<span class="hl">\1</span>', e(s))


# ---------------------------------------------------------------- palettes
# bg, bg2, card, line, text, muted, a1, a2 (accent gradient), ok
PALETTES = {
    "night-blue": ("#0b0d12", "#12151d", "#171b25", "#262c3a", "#eef1f7", "#9aa3b5", "#2f7bff", "#38c6ff", "dark"),
    "night-teal": ("#081110", "#0e1a19", "#13221f", "#22362f", "#e9f4f1", "#93aba4", "#14b8a6", "#5eead4", "dark"),
    "night-orange": ("#100c09", "#18120e", "#201812", "#33271d", "#f6efe8", "#b3a395", "#ff6a1a", "#ffb547", "dark"),
    "night-lime": ("#0a0f08", "#11180d", "#162012", "#26341e", "#eef6e9", "#9fb294", "#65c728", "#c2f04a", "dark"),
    "night-red": ("#0e0a0b", "#171012", "#1f1517", "#352428", "#f6eef0", "#b39ca1", "#ef3b3b", "#ff8a4c", "dark"),
    "night-violet": ("#0d0b12", "#15121d", "#1b1726", "#2d2740", "#f1eef8", "#a49cb8", "#8b5cf6", "#e879f9", "dark"),
    "day-sky": ("#f5f8fb", "#eaf0f6", "#ffffff", "#d7e1eb", "#0f1b2a", "#526173", "#0a6cdc", "#16a3e8", "light"),
    "day-green": ("#f6f8f2", "#ebf0e2", "#ffffff", "#d9e2cb", "#17220f", "#56654a", "#2f7d1f", "#7fb800", "light"),
    "day-coral": ("#fbf6f3", "#f4ebe5", "#ffffff", "#ead9cf", "#24160f", "#6c584c", "#d9481c", "#f08a24", "light"),
    "day-rose": ("#fcf6f7", "#f6eaed", "#ffffff", "#ecd6dc", "#2a1219", "#73545d", "#c2185b", "#ee6d9a", "light"),
    "day-mint": ("#f3f9f7", "#e5f2ee", "#ffffff", "#cfe5de", "#0d221c", "#4c6760", "#0d8a6f", "#2bb5a0", "light"),
    "day-navy": ("#f6f7fb", "#ebeef6", "#ffffff", "#d8deec", "#111a33", "#535d78", "#1d3fa8", "#d6402b", "light"),
}

FONTS = {
    "archivo": ("'Archivo Black', Inter, sans-serif", "family=Archivo+Black&family=Inter:wght@400;500;600;700", 400),
    "bebas": ("'Bebas Neue', 'Arial Narrow', sans-serif", "family=Bebas+Neue&family=Inter:wght@400;500;600;700", 400),
    "outfit": ("'Outfit', Inter, sans-serif", "family=Outfit:wght@600;800&family=Inter:wght@400;500;600;700", 800),
    "sora": ("'Sora', Inter, sans-serif", "family=Sora:wght@600;800&family=Inter:wght@400;500;600;700", 800),
    "anton": ("'Anton', Impact, sans-serif", "family=Anton&family=Inter:wght@400;500;600;700", 400),
    "fraunces": ("'Fraunces', Georgia, serif", "family=Fraunces:opsz,wght@9..144,700&family=Inter:wght@400;500;600;700", 700),
    "grotesk": ("'Space Grotesk', Inter, sans-serif", "family=Space+Grotesk:wght@600;700&family=Inter:wght@400;500;600;700", 700),
    "barlow": ("'Barlow Condensed', 'Arial Narrow', sans-serif", "family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500;600;700", 800),
}

# ---------------------------------------------------------------- icons (24x24 stroke paths)
ICONS = {
    "house": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "drive": '<path d="M4 20L9 4h6l5 16"/><path d="M12 6v2M12 11v2M12 16v2"/>',
    "roof": '<path d="M2 13L12 5l10 8"/><path d="M5 11v8h14v-8"/><path d="M8 15h8"/>',
    "gutter": '<path d="M3 6h18v3a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3z"/><path d="M17 12v8"/><path d="M15 20h4"/>',
    "fence": '<path d="M5 21V7l2-3 2 3v14M15 21V7l2-3 2 3v14M3 10h18M3 16h18"/>',
    "car": '<path d="M5 17h14l-1.5-6h-11zM7 17v2M17 17v2M6.5 11l1.5-4h8l1.5 4"/><circle cx="8" cy="14" r="1"/><circle cx="16" cy="14" r="1"/>',
    "boat": '<path d="M3 16l2 4h14l2-4z"/><path d="M12 3v13M12 4l6 9h-6"/>',
    "window": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M12 3v18M4 12h16"/>',
    "truck": '<path d="M2 7h11v9H2zM13 10h5l3 3v3h-8z"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "trash": '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/><path d="M10 11v6M14 11v6"/>',
    "broom": '<path d="M14 3l-4 9"/><path d="M6 12h8l2 9H4z"/><path d="M8 16v5M12 16v5"/>',
    "spark": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    "leaf": '<path d="M5 19c0-9 6-14 15-15-1 9-6 15-15 15z"/><path d="M5 19l8-8"/>',
    "tree": '<path d="M12 22v-6"/><path d="M12 2l6 8h-3l4 6H5l4-6H6z"/>',
    "roller": '<rect x="3" y="3" width="15" height="6" rx="1"/><path d="M18 6h3v5h-9v3"/><rect x="10" y="14" width="4" height="7" rx="1"/>',
    "brush": '<path d="M14 4l6 6-8 8-6-6z"/><path d="M6 12l-3 3c-1 1-1 3 0 4s3 1 4 0l3-3"/>',
    "drop": '<path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11z"/>',
    "wrench": '<path d="M14 6a4 4 0 0 0 5 5l-9 9a2 2 0 0 1-3-3l9-9a4 4 0 0 0-2-2z"/>',
    "hammer": '<path d="M14 4l6 6-3 3-6-6z"/><path d="M11 7L3 15l3 3 8-8"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "snow": '<path d="M12 2v20M4 6l16 12M20 6L4 18"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "building": '<path d="M4 21V5l8-3v19M12 9l8 3v9M2 21h20M7 9h2M7 13h2M7 17h2"/>',
    "cake": '<path d="M4 21h16v-8H4z"/><path d="M4 16c2 1 4 1 6 0s4-1 6 0 2 1 4 0"/><path d="M12 13V9M12 6v.01"/>',
    "food": '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10"/><path d="M17 3c-2 2-2 6 0 8v10"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "mail": '<path d="M4 5h16v14H4zM4 6l8 7 8-7"/>',
    "fb": '<path d="M15 3h-3a4 4 0 0 0-4 4v3H6v4h2v7h4v-7h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "ig": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".5"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "pool": '<path d="M2 18c2 1.5 4 1.5 6 0s4-1.5 6 0 4 1.5 6 0"/><path d="M2 14c2 1.5 4 1.5 6 0s4-1.5 6 0 4 1.5 6 0"/><path d="M8 12V5a2 2 0 0 1 4 0M16 12V5a2 2 0 0 0-4 0"/>',
    "floor": '<path d="M3 20l4-12h10l4 12z"/><path d="M8 14h.01M12 12h.01M15 16h.01M10 17h.01M14 13h.01"/>',
    "dog": '<path d="M5 10l-1-6 4 3h8l4-3-1 6"/><path d="M5 10c0 6 3 10 7 10s7-4 7-10"/><path d="M10 13h.01M14 13h.01M11 16h2"/>',
    "scissors": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4L8.1 15.9M14.5 14.5L20 20M8.1 8.1L12 12"/>',
    "bug": '<path d="M8 8a4 4 0 0 1 8 0v8a4 4 0 0 1-8 0z"/><path d="M12 8v12M4 12h4M16 12h4M5 6l3 3M19 6l-3 3M5 19l3-3M19 19l-3-3"/>',
}
KEYWORDS = [
    ("roof", "roof"), ("gutter", "gutter"), ("fence", "fence"), ("deck", "fence"), ("patio", "drive"),
    ("driveway", "drive"), ("concrete", "drive"), ("sidewalk", "drive"), ("pavers", "drive"), ("parking", "drive"),
    ("boat", "boat"), ("rv", "truck"), ("fleet", "truck"), ("ceramic", "shield"), ("coating", "shield"),
    ("interior", "spark"), ("exterior", "car"), ("detail", "car"), ("car", "car"), ("auto", "car"), ("truck", "truck"),
    ("window", "window"), ("junk", "trash"), ("haul", "truck"), ("debris", "trash"), ("demolition", "hammer"),
    ("move-out", "house"), ("move out", "house"), ("deep", "spark"), ("office", "building"), ("commercial", "building"),
    ("airbnb", "cal"), ("recurring", "cal"), ("weekly", "cal"), ("mow", "leaf"), ("lawn", "leaf"), ("landscap", "leaf"),
    ("mulch", "leaf"), ("sod", "leaf"), ("hedge", "leaf"), ("leaf", "leaf"), ("tree", "tree"), ("stump", "tree"),
    ("paint", "roller"), ("stain", "brush"), ("cabinet", "brush"), ("drywall", "hammer"), ("repair", "wrench"),
    ("plumb", "drop"), ("water", "drop"), ("electric", "bolt"), ("light", "bolt"), ("hvac", "snow"), ("a/c", "snow"),
    ("ac ", "snow"), ("heat", "sun"), ("pool", "pool"), ("epoxy", "floor"), ("floor", "floor"), ("garage", "floor"),
    ("cake", "cake"), ("cupcake", "cake"), ("cookie", "cake"), ("dessert", "cake"), ("cater", "food"), ("menu", "food"),
    ("plate", "food"), ("taco", "food"), ("bbq", "food"), ("pet", "dog"), ("dog", "dog"), ("groom", "scissors"),
    ("hair", "scissors"), ("cut", "scissors"), ("pest", "bug"), ("house", "house"), ("home", "house"), ("siding", "house"),
    ("soft wash", "drop"), ("pressure", "drop"), ("power wash", "drop"), ("install", "hammer"), ("weld", "bolt"),
    ("brake", "wrench"), ("oil", "wrench"), ("diagnos", "wrench"), ("engine", "wrench"), ("mobile", "truck"),
]


def icon_for(title, default="star"):
    t = title.lower()
    for k, v in KEYWORDS:
        if k in t:
            return v
    return default


def svg(name, cls=""):
    return f'<svg viewBox="0 0 24 24"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} aria-hidden="true">{ICONS.get(name, ICONS["star"])}</svg>'


# ---------------------------------------------------------------- textures for before/after
def noise(seed, freq, matrix):
    return ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E"
            f"%3CfeTurbulence type='fractalNoise' baseFrequency='{freq}' numOctaves='5' seed='{seed}'/%3E%3CfeColorMatrix values='{matrix}'/%3E"
            "%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\") 0 0/300px")


GRIME = noise(7, ".03", "0 0 0 0 .18  0 0 0 0 .2  0 0 0 0 .12  0 0 0 -2.4 1.7")
RUST = noise(7, ".035", "0 0 0 0 .55  0 0 0 0 .25  0 0 0 0 .08  0 0 0 -2.2 1.6")
WEED = noise(3, ".06", "0 0 0 0 .38  0 0 0 0 .42  0 0 0 0 .12  0 0 0 -2 1.5")
ALGAE = noise(11, ".02", "0 0 0 0 .2  0 0 0 0 .35  0 0 0 0 .12  0 0 0 -2.2 1.6")
SWIRL = noise(5, ".012", "0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -3 1.4")
SPECK = noise(9, ".9", "0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 -6 3.2")

BA = {
    # preset: (before css, after css, before label, after label)
    "concrete": (f"radial-gradient(circle at 20% 70%,rgba(40,44,30,.75) 0 9%,transparent 10%),radial-gradient(circle at 75% 30%,rgba(30,34,22,.7) 0 12%,transparent 13%),{GRIME},repeating-linear-gradient(90deg,transparent 0 24.6%,rgba(0,0,0,.35) 24.6% 25%),linear-gradient(135deg,#6d6f62,#4d5045)",
                 f"{SPECK},repeating-linear-gradient(90deg,transparent 0 24.6%,rgba(0,0,0,.18) 24.6% 25%),linear-gradient(135deg,#d9d9d2,#b9bab2)",
                 "Before", "After"),
    "siding": (f"{ALGAE},repeating-linear-gradient(180deg,#b9bfae 0 22px,#8f9784 22px 24px)",
               "linear-gradient(115deg,rgba(255,255,255,.4) 0 10%,transparent 10%),repeating-linear-gradient(180deg,#f3f5f2 0 22px,#cfd5d0 22px 24px)",
               "Before", "After"),
    "roof": (f"repeating-linear-gradient(90deg,transparent 0 10px,rgba(0,0,0,.08) 10px 12px),{ALGAE},repeating-linear-gradient(180deg,#3a3d3a 0 18px,#262826 18px 20px)",
             "repeating-linear-gradient(90deg,transparent 0 10px,rgba(0,0,0,.08) 10px 12px),repeating-linear-gradient(180deg,#5b6068 0 18px,#3f434a 18px 20px)",
             "Before", "After"),
    "deck": (f"{GRIME},repeating-linear-gradient(90deg,#8d877c 0 46px,#5f5a52 46px 49px)",
             "linear-gradient(115deg,rgba(255,255,255,.18) 0 12%,transparent 12%),repeating-linear-gradient(90deg,#a8663a 0 46px,#6b3b1f 46px 49px)",
             "Before", "After"),
    "paint": (f"{SWIRL},radial-gradient(circle at 30% 40%,#3a3f47,#24272c)",
              "linear-gradient(118deg,rgba(255,255,255,.55) 0 8%,transparent 8% 22%,rgba(255,255,255,.25) 22% 24%,transparent 24%),radial-gradient(circle at 30% 30%,#1e3f8a,#0b1530 70%)",
              "Before", "After"),
    "interior": (f"radial-gradient(circle at 30% 60%,rgba(70,55,40,.8) 0 6%,transparent 7%),radial-gradient(circle at 70% 35%,rgba(60,48,35,.7) 0 8%,transparent 9%),{GRIME},repeating-linear-gradient(90deg,#4a4540 0 3px,#3d3934 3px 6px)",
                 "repeating-linear-gradient(90deg,#2e2f33 0 3px,#26272b 3px 6px)", "Before", "After"),
    "lawn": (f"{WEED},radial-gradient(circle at 20% 30%,#a59a4a 0 6%,transparent 7%),radial-gradient(circle at 70% 70%,#8c8a3c 0 8%,transparent 9%),linear-gradient(#6e7a35,#4f5a25)",
             "repeating-linear-gradient(90deg,#3f8f2e 0 12.5%,#4fa63a 12.5% 25%)", "Before", "After"),
    "pool": (f"{ALGAE},linear-gradient(#5c7a3a,#3d5527)",
             "repeating-radial-gradient(circle at 30% 40%,rgba(255,255,255,.18) 0 2px,transparent 3px 18px),linear-gradient(#3cc3e8,#0b7fb8)", "Before", "After"),
    "metal": (f"radial-gradient(circle at 15% 25%,#4e230a 0 7%,transparent 8%),radial-gradient(circle at 60% 70%,#57290c 0 11%,transparent 12%),{RUST},linear-gradient(135deg,#9a5520,#5a2a0c)",
              "linear-gradient(115deg,rgba(255,255,255,.35) 0 12%,transparent 12% 30%,rgba(255,255,255,.18) 30% 33%,transparent 33%),repeating-linear-gradient(90deg,#b8bec7 0 2px,#a9b0ba 2px 4px),linear-gradient(#cfd4db,#8b929c)",
              "Before", "After"),
    "yard": (f"radial-gradient(circle at 25% 65%,#5a4630 0 9%,transparent 10%),radial-gradient(circle at 65% 40%,#4b3a28 0 12%,transparent 13%),radial-gradient(circle at 80% 75%,#6a5335 0 7%,transparent 8%),{WEED},linear-gradient(#6b6a3a,#4a4a27)",
             "repeating-linear-gradient(90deg,#3f8f2e 0 12.5%,#4fa63a 12.5% 25%)", "Before", "After"),
}

# ---------------------------------------------------------------- industries
IND = {
    "pressure": dict(label="Pressure Washing", pals=["night-blue", "night-teal", "day-sky", "day-navy"], fonts=["archivo", "outfit", "barlow"],
                     module="ba", ba="concrete", hero="sweep", cta="Get a Free Quote", chips_title="What we clean",
                     ba_title="Drag to see the difference.", ba_text="Years of grime, algae and oil stains lifted off. The surface underneath looks new again.",
                     steps=[("Reach Out", "Call, text or message us with a few photos of the job."), ("Free Quote", "We look it over and give you a clear price."),
                            ("We Wash", "Pressure or soft wash, matched to the surface."), ("Looks New", "Clean, bright surfaces and a tidy site when we leave.")]),
    "detail": dict(label="Auto Detailing", pals=["night-blue", "night-red", "night-violet", "night-orange"], fonts=["anton", "bebas", "sora"],
                   module="ba", ba="paint", hero="sweep", cta="Book a Detail", chips_title="What we detail",
                   ba_title="Drag to see the shine.", ba_text="Swirls, dust and dull paint on one side. A deep, glossy finish on the other.",
                   steps=[("Pick a Service", "Tell us your vehicle and what it needs."), ("Book a Time", "Choose a day that works for you."),
                          ("We Detail", "Careful hand work, inside and out."), ("Drive Away Happy", "A car that looks and smells fresh.")]),
    "lawn": dict(label="Lawn Care", pals=["day-green", "night-lime", "day-mint"], fonts=["outfit", "barlow", "grotesk"],
                 module="ba", ba="lawn", hero="sweep", cta="Get a Free Quote", chips_title="What we do",
                 ba_title="Drag to see the cut.", ba_text="Overgrown and patchy on one side. Clean lines and an even cut on the other.",
                 steps=[("Reach Out", "Call or message us with your address."), ("Free Quote", "We give you a clear price for your yard."),
                        ("We Get to Work", "Mowing, edging and cleanup on your schedule."), ("Enjoy Your Yard", "A neat, healthy lawn you're proud of.")]),
    "landscape": dict(label="Landscaping", pals=["day-green", "night-lime", "day-mint"], fonts=["fraunces", "outfit", "grotesk"],
                      module="ba", ba="yard", hero="sweep", cta="Get a Free Quote", chips_title="What we do",
                      ba_title="Drag to see the difference.", ba_text="Weeds and bare patches on one side. A finished, cared-for yard on the other.",
                      steps=[("Reach Out", "Tell us about your yard and what you want."), ("Plan & Quote", "We walk the property and give you a price."),
                             ("We Build It", "Planting, beds, sod and cleanup."), ("Enjoy It", "A yard that looks good every time you pull in.")]),
    "junk": dict(label="Junk Removal", pals=["night-orange", "day-coral", "night-lime", "day-navy"], fonts=["anton", "archivo", "barlow"],
                 module="load", hero="icon", hero_icon="truck", cta="Get a Quote", chips_title="What we haul",
                 steps=[("Send Photos", "Text or message us pictures of what needs to go."), ("Get a Price", "We quote by how much space it takes up."),
                        ("We Haul It", "We do the lifting and loading."), ("Swept Clean", "The space is cleared out and swept.")]),
    "clean": dict(label="Cleaning Service", pals=["day-mint", "day-sky", "day-rose", "night-teal"], fonts=["outfit", "sora", "fraunces"],
                  module="rooms", hero="icon", hero_icon="spark", cta="Request a Quote", chips_title="Cleaning for",
                  steps=[("Reach Out", "Tell us about your space and how often."), ("Get a Quote", "We give you a clear, upfront price."),
                         ("We Clean", "Top to bottom, room by room."), ("Come Home to Clean", "Fresh, tidy and ready to enjoy.")]),
    "paint": dict(label="Painting", pals=["day-navy", "day-coral", "night-violet", "day-sky"], fonts=["fraunces", "grotesk", "outfit"],
                  module="swatch", hero="icon", hero_icon="roller", cta="Get a Free Estimate", chips_title="What we paint",
                  steps=[("Reach Out", "Tell us about the rooms or exterior."), ("Free Estimate", "We look at the job and give you a price."),
                         ("Prep & Paint", "Careful prep, clean lines, two coats where it counts."), ("Walkthrough", "We check every wall with you.")]),
    "epoxy": dict(label="Epoxy Floors", pals=["night-blue", "night-orange", "night-violet"], fonts=["anton", "archivo", "sora"],
                  module="flake", hero="icon", hero_icon="floor", cta="Get a Free Quote", chips_title="Floors we coat",
                  steps=[("Reach Out", "Send the size of the space and a photo."), ("Pick Your Finish", "Choose a color and flake blend."),
                         ("Prep & Coat", "Grind, repair and coat the concrete."), ("Back in Use", "A tough, glossy floor that's easy to clean.")]),
    "fence": dict(label="Fencing", pals=["day-navy", "night-orange", "day-green"], fonts=["barlow", "archivo", "grotesk"],
                  module="builder", hero="icon", hero_icon="fence", cta="Get a Free Estimate", chips_title="What we build",
                  steps=[("Reach Out", "Tell us the length and style you want."), ("Free Estimate", "We measure and give you a price."),
                         ("We Build", "Posts set, panels hung, gates fitted."), ("Done Right", "A solid fence built to last.")]),
    "pool": dict(label="Pool Service", pals=["day-sky", "night-teal", "day-mint"], fonts=["outfit", "sora", "grotesk"],
                 module="ba", ba="pool", hero="sweep", cta="Get a Quote", chips_title="What we do",
                 ba_title="Drag to see the water.", ba_text="Green and cloudy on one side. Clear and blue on the other.",
                 steps=[("Reach Out", "Tell us about your pool."), ("Get a Quote", "Weekly service or a one-time cleanup."),
                        ("We Service It", "Clean, balance and check the equipment."), ("Dive In", "Clear water, ready to swim.")]),
    "tree": dict(label="Tree Service", pals=["day-green", "night-lime", "night-orange"], fonts=["barlow", "anton", "outfit"],
                 module="builder", hero="icon", hero_icon="tree", cta="Get a Free Estimate", chips_title="What we do",
                 steps=[("Reach Out", "Send photos of the trees or the damage."), ("Free Estimate", "We look it over and quote the job."),
                        ("We Cut & Clear", "Safe cutting, careful around your property."), ("Clean Yard", "Debris hauled off and the area raked.")]),
    "handyman": dict(label="Handyman", pals=["day-navy", "night-orange", "day-coral", "night-blue"], fonts=["barlow", "grotesk", "archivo"],
                     module="builder", hero="icon", hero_icon="hammer", cta="Get a Quote", chips_title="Jobs we take",
                     steps=[("Make a List", "Tell us everything on your to-do list."), ("Get a Quote", "One clear price for the visit."),
                            ("We Fix It", "Show up, do the work, clean up."), ("Check It Off", "Your list, done.")]),
    "mechanic": dict(label="Mobile Mechanic", pals=["night-red", "night-orange", "night-blue"], fonts=["anton", "barlow", "archivo"],
                     module="builder", hero="icon", hero_icon="wrench", cta="Request Service", chips_title="We work on",
                     steps=[("Tell Us the Problem", "Year, make, model and what it's doing."), ("Get a Quote", "A clear price before we start."),
                            ("We Come to You", "Repairs at your home or work."), ("Back on the Road", "Fixed right, and explained.")]),
    "roof": dict(label="Roofing", pals=["day-navy", "night-red", "night-blue"], fonts=["barlow", "archivo", "sora"],
                 module="builder", hero="icon", hero_icon="roof", cta="Free Roof Inspection", chips_title="What we do",
                 steps=[("Reach Out", "Call or message about your roof."), ("Inspection", "We look it over and show you what we find."),
                        ("Clear Quote", "A written price for the work."), ("Protected", "A roof you don't have to worry about.")]),
    "hvac": dict(label="Heating & Air", pals=["day-sky", "night-blue", "day-navy"], fonts=["sora", "outfit", "barlow"],
                 module="builder", hero="icon", hero_icon="snow", cta="Request Service", chips_title="What we do",
                 steps=[("Call or Message", "Tell us what your system is doing."), ("Diagnosis", "We find the problem and explain it."),
                        ("Clear Price", "You approve the price before work starts."), ("Comfortable Again", "Cool in summer, warm in winter.")]),
    "food": dict(label="Food", pals=["night-orange", "night-red", "day-coral"], fonts=["anton", "bebas", "fraunces"],
                 module="menu", hero="icon", hero_icon="food", cta="Order Now", chips_title="Find us for",
                 steps=[("Check the Menu", "See what's cooking this week."), ("Find Us", "Follow our page for today's spot."),
                        ("Order Up", "Made fresh while you wait."), ("Come Back Hungry", "Bring a friend next time.")]),
    "cake": dict(label="Bakery", pals=["day-rose", "day-coral", "night-violet"], fonts=["fraunces", "outfit", "sora"],
                 module="menu", hero="icon", hero_icon="cake", cta="Order a Cake", chips_title="Made for",
                 steps=[("Share Your Idea", "Date, size, flavor and theme."), ("Get a Quote", "We confirm the details and price."),
                        ("We Bake", "Made from scratch for your day."), ("Celebrate", "Pick up and enjoy.")]),
    "pet": dict(label="Pet Grooming", pals=["day-rose", "day-mint", "day-sky"], fonts=["outfit", "fraunces", "sora"],
                module="builder", hero="icon", hero_icon="dog", cta="Book a Groom", chips_title="We groom",
                steps=[("Reach Out", "Tell us your pet's breed and size."), ("Book a Time", "Pick a day that works."),
                       ("Pamper Time", "Bath, cut and finishing touches."), ("Fresh & Happy", "A clean pup, ready for cuddles.")]),
}


def pick(seq, key, salt):
    h = int(hashlib.md5((key + salt).encode()).hexdigest(), 16)
    return seq[h % len(seq)]


# ---------------------------------------------------------------- modules
def mod_ba(b, ind):
    pre = b.get("ba", ind.get("ba", "concrete"))
    before, after, bl, al = BA[pre]
    title = b.get("ba_title", ind.get("ba_title", "Drag to see the difference."))
    text = b.get("ba_text", ind.get("ba_text", ""))
    return f'''<section id="results" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">Before &amp; After</span><h2>{e(title)}</h2><p>{e(text)}</p></div>
    <div class="ba reveal" id="ba">
      <div class="layer after"></div><div class="layer before"></div>
      <span class="lbl b">{bl}</span><span class="lbl a">{al}</span><div class="handle"></div>
      <input type="range" min="0" max="100" value="50" aria-label="Before and after comparison slider" id="baRange">
    </div>
    <p class="ba-note">Illustration. Real job photos from {e(b["name"])} would go here.</p>
  </div>
</section>''', "results", "Results"


def mod_load(b, ind):
    sizes = [("Single item", 8), ("1/4 load", 25), ("1/2 load", 50), ("3/4 load", 75), ("Full load", 100)]
    btns = "".join(f'<button type="button" class="opt{" on" if i == 1 else ""}" data-fill="{p}" data-name="{n}">{n}</button>' for i, (n, p) in enumerate(sizes))
    return f'''<section id="estimate" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">How Much Is It?</span><h2>Pick your load size.</h2><p>Junk removal is priced by how much room it takes up in the truck. Tap a size and we'll put it in your quote request.</p></div>
    <div class="loadbox reveal">
      <svg viewBox="0 0 400 170" class="truck" aria-hidden="true">
        <rect x="20" y="40" width="250" height="90" rx="6" class="t-bed"/>
        <rect x="24" y="44" width="242" height="82" rx="4" class="t-in"/>
        <rect id="fill" x="24" y="44" width="60" height="82" rx="4" class="t-fill"/>
        <path d="M270 70h60l40 30v30H270z" class="t-cab"/><path d="M285 80h38l25 20h-63z" class="t-win"/>
        <circle cx="80" cy="140" r="20" class="t-wh"/><circle cx="310" cy="140" r="20" class="t-wh"/>
        <circle cx="80" cy="140" r="8" class="t-hub"/><circle cx="310" cy="140" r="8" class="t-hub"/>
      </svg>
      <div class="opts" id="loadOpts">{btns}</div>
      <p class="ba-note" id="loadNote">1/4 load selected. Pricing comes from {e(b["name"])} after they see your photos.</p>
    </div>
  </div>
</section>''', "estimate", "Pricing"


def mod_rooms(b, ind):
    rooms = b.get("rooms") or [
        ("Kitchen", ["Counters and backsplash wiped", "Stovetop and outside of appliances", "Sink scrubbed and shined", "Floors swept and mopped"]),
        ("Bathrooms", ["Toilet, tub and shower scrubbed", "Mirrors and fixtures polished", "Counters and sink cleaned", "Floors washed"]),
        ("Bedrooms", ["Dusting surfaces and baseboards", "Beds made", "Mirrors and glass cleaned", "Floors vacuumed"]),
        ("Living Areas", ["Dusting and wiping surfaces", "Cushions straightened", "Trash taken out", "Floors vacuumed and mopped"]),
    ]
    tabs = "".join(f'<button type="button" class="opt{" on" if i == 0 else ""}" data-room="{i}">{e(r)}</button>' for i, (r, _) in enumerate(rooms))
    lists = "".join(f'<ul class="check{"" if i == 0 else " hide"}" data-list="{i}">' + "".join(f'<li><label><input type="checkbox" checked> {e(x)}</label></li>' for x in items) + "</ul>" for i, (_, items) in enumerate(rooms))
    return f'''<section id="checklist" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">Room by Room</span><h2>Here's what a clean looks like.</h2><p>A typical checklist. Tell {e(b["name"])} what matters most in your home and they'll tailor it.</p></div>
    <div class="roombox reveal"><div class="opts" id="roomTabs">{tabs}</div>{lists}</div>
  </div>
</section>''', "checklist", "Checklist"


def mod_swatch(b, ind):
    cols = [("Agreeable Gray", "#d1cbc1"), ("Naval", "#2f3d4c"), ("Sage", "#a7b49a"), ("Alabaster", "#efe9dd"),
            ("Terracotta", "#c46a4a"), ("Charcoal", "#3b3b3b"), ("Sky", "#9cc3dd"), ("Butter", "#f1d98a")]
    btns = "".join(f'<button type="button" class="sw{" on" if i == 0 else ""}" style="--c:{c}" data-c="{c}" data-name="{n}" aria-label="{n}"></button>' for i, (n, c) in enumerate(cols))
    return f'''<section id="colors" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">Try a Color</span><h2>See it before we paint it.</h2><p>Tap a swatch to preview a color. Common color names shown; {e(b["name"])} can match any brand.</p></div>
    <div class="swbox reveal">
      <svg viewBox="0 0 400 240" class="housev" aria-hidden="true">
        <rect x="0" y="210" width="400" height="30" class="h-ground"/>
        <path id="wall" d="M70 210V110L200 40l130 70v100z" style="fill:#d1cbc1"/>
        <path d="M60 116L200 36l140 80" class="h-roof"/>
        <rect x="175" y="140" width="50" height="70" class="h-door"/>
        <rect x="100" y="130" width="45" height="40" class="h-win"/><rect x="255" y="130" width="45" height="40" class="h-win"/>
        <path d="M122 130v40M100 150h45M277 130v40M255 150h45" class="h-mull"/>
      </svg>
      <div class="sws">{btns}</div><p class="ba-note" id="swName">Agreeable Gray</p>
    </div>
  </div>
</section>''', "colors", "Colors"


def mod_flake(b, ind):
    blends = [("Domino", ["#111", "#eee", "#777"]), ("Gravel", ["#5b5650", "#a39a8c", "#e2dccf"]), ("Nightfall", ["#1b2440", "#5b6a8f", "#c9d1e6"]),
              ("Tidal Wave", ["#1d4e6b", "#7fb3c9", "#e8f1f4"]), ("Saddle Tan", ["#5a3d24", "#b08356", "#ead7bd"]), ("Cabin Fever", ["#3a3a3a", "#8c6b4a", "#d9cbb5"])]
    btns = "".join(f'<button type="button" class="opt{" on" if i == 0 else ""}" data-c="{",".join(c)}" data-name="{n}">{n}</button>' for i, (n, c) in enumerate(blends))
    return f'''<section id="finishes" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">Pick a Finish</span><h2>Choose your flake blend.</h2><p>Tap a blend to preview it on the floor. Popular blend names shown; ask {e(b["name"])} what they carry.</p></div>
    <div class="flakebox reveal"><canvas id="floor" width="800" height="360" aria-label="Floor finish preview"></canvas><div class="opts" id="flakeOpts">{btns}</div></div>
  </div>
</section>''', "finishes", "Finishes"


def mod_builder(b, ind):
    items = b.get("builder") or [s[0] for s in b["services"]]
    chips = "".join(f'<button type="button" class="pick" aria-pressed="false">{e(x)}</button>' for x in items)
    return f'''<section id="quote-builder" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">Build Your Request</span><h2>What can we help with?</h2><p>Tap everything you need. We'll add it to your quote request below.</p></div>
    <div class="builder reveal"><div class="picks" id="picks">{chips}</div><p class="ba-note" id="pickNote">Nothing selected yet.</p></div>
  </div>
</section>''', "quote-builder", "Get a Quote"


def mod_menu(b, ind):
    items = b.get("menu") or [[s[0], s[1]] for s in b["services"]]
    cards = "".join(f'<div class="mi reveal"><h3>{e(n)}</h3>{f"<p>{e(d)}</p>" if d else ""}</div>' for n, d in items)
    t = b.get("menu_title", "On the menu")
    return f'''<section id="menu" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">Menu</span><h2>{e(t)}</h2><p>{e(b.get("menu_text", "Items from " + b["name"] + "'s posts. The full menu with prices would go here."))}</p></div>
    <div class="menu">{cards}</div>
  </div>
</section>''', "menu", "Menu"


MODULES = {"ba": mod_ba, "load": mod_load, "rooms": mod_rooms, "swatch": mod_swatch, "flake": mod_flake, "builder": mod_builder, "menu": mod_menu}


def hero_visual(b, ind):
    if ind.get("hero") == "sweep":
        pre = b.get("ba", ind.get("ba", "concrete"))
        before, after, _, _ = BA[pre]
        return f'''<div class="sweep-card" aria-hidden="true">
      <div class="s-after"></div><div class="s-before"></div><div class="beam"></div>
      <span class="tag l">CLEAN</span><span class="tag r">BEFORE</span></div>'''
    ic = b.get("hero_icon", ind.get("hero_icon", "star"))
    tags = b["badges"][:3]
    tag_html = "".join(f'<span class="ftag f{i}">{e(t)}</span>' for i, t in enumerate(tags))
    return f'''<div class="icon-card" aria-hidden="true"><div class="ring r1"></div><div class="ring r2"></div>
      <div class="big-ico">{svg(ic)}</div>{tag_html}</div>'''


FEATURE_LABEL = {"ba": "A before-and-after slider", "load": "A load-size picker", "rooms": "A room-by-room checklist",
                 "swatch": "A paint color previewer", "flake": "A floor finish previewer", "builder": "A tap-to-pick quote builder",
                 "menu": "Your menu, front and center"}
PRESENCE = {
    "none": ("No website found", "Searching for the business turns up the Facebook page, not a site of its own."),
    "deadsite": ("Broken website link", "The website link on the Facebook page goes to a business.site address. Google shut those sites down in 2024, so anyone who taps it hits a dead end."),
    "linktree": ("A Linktree, not a website", "The Facebook page links to a Linktree: a list of links, with no services, photos or quote form."),
    "booking": ("A booking page, not a website", "The Facebook page links to a booking page. It takes appointments but doesn't show services, work or the area served."),
    "directory": ("Directory listings only", "Outside Facebook, the business shows up only on directory listings, not on a site of its own."),
}
OK = '<span class="yes" aria-label="Yes">&#10003;</span>'
NO = '<span class="no" aria-label="No">&#10005;</span>'


def presence_section(b, ind, module):
    kind = b.get("presence", "none")
    title, detail = PRESENCE[kind]
    short = b.get("short", b["name"])
    trade = ind["label"].lower()
    stem = ""
    for w in slugify(short).split("-"):
        if stem and len(stem) + len(w) > 22:
            break
        stem += w
    domain = b.get("domain_example", stem + ".com")
    rev = b.get("fb_reviews")
    today = [(OK, "Facebook page", "Contact details and posts" + (f" &middot; {e(rev)}" if rev else "")),
             (NO, e(title), e(detail)),
             (NO, "Quote requests", "Come in as Facebook messages or calls, without the job details up front")]
    site = [(OK, "Your own web address", f"Something like {e(domain)} (example), on cards, your truck and invoices"),
            (OK, "A real site in Google results", f"Built for people searching for {e(trade)} in {e(b['city'])}"),
            (OK, "Everything in one place", "Services, service area, how it works and contact info"),
            (OK, FEATURE_LABEL[module], "Something a Facebook page can't do"),
            (OK, "Quote form and tap-to-call", "Requests arrive with the details you need to price the job")]
    li = lambda rows: "".join(f'<li>{m}<div><b>{t}</b><span>{d}</span></div></li>' for m, t, d in rows)
    rows = [("Your own web address", NO, OK), ("Your own site in Google results", NO, OK),
            ("Easy to view without logging in to Facebook", '<span class="part">Login pop-ups</span>', OK),
            ("No ads or other businesses' pages next to yours", NO, OK),
            ("Services, area and contact laid out in one place", '<span class="part">Short About section</span>', OK),
            (FEATURE_LABEL[module], NO, OK), ("Quote requests with job details", '<span class="part">Messages only</span>', OK)]
    table = "".join(f"<tr><td>{e(r)}</td><td>{a}</td><td>{c}</td></tr>" for r, a, c in rows)
    return f'''<section id="online" class="alt">
  <div class="wrap">
    <div class="sec-head center reveal"><span class="eyebrow">For {e(short)}: online today vs. this site</span><h2>Where you stand online, and what this site adds.</h2>
      <p>What we found when we looked {e(short)} up in November 2026, next to what this website gives you.</p></div>
    <div class="vs-grid">
      <div class="vs-card today reveal"><span class="vs-tag">Today</span><h3>Facebook only</h3><ul class="vs-list">{li(today)}</ul></div>
      <div class="vs-card next reveal"><span class="vs-tag">With this website</span><h3>A home base online</h3><ul class="vs-list">{li(site)}</ul></div>
    </div>
    <div class="vs-scroll reveal"><table class="vs-table"><thead><tr><th>Side by side</th><th><span class="lg">Facebook page only</span><span class="sm">Facebook only</span></th><th><span class="lg">Facebook + this website</span><span class="sm">+ Website</span></th></tr></thead><tbody>{table}</tbody></table></div>
    <p class="ba-note">Keep the Facebook page for posts and reviews. A website works alongside it.</p>
  </div>
</section>'''


# ---------------------------------------------------------------- page
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:Inter,system-ui,sans-serif;line-height:1.6;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img,svg,canvas{display:block;max-width:100%}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
h1,h2,h3{font-family:var(--disp);font-weight:var(--dw);line-height:1.08;letter-spacing:-.01em}
.eyebrow{display:inline-block;color:var(--a1);font-weight:700;font-size:.78rem;letter-spacing:.18em;text-transform:uppercase;margin-bottom:14px}
.btn{display:inline-flex;align-items:center;gap:10px;padding:14px 26px;border-radius:999px;font-weight:700;transition:transform .2s,box-shadow .2s,background .2s;border:0;cursor:pointer;font-size:1rem;font-family:inherit}
.btn-primary{background:linear-gradient(135deg,var(--a1),var(--a2));color:var(--on);box-shadow:0 10px 30px -10px var(--a1)}
.btn-primary:hover{transform:translateY(-2px)}
.btn-ghost{border:1.5px solid var(--line);color:var(--text)}
.btn-ghost:hover{border-color:var(--a1)}
.demo{background:var(--a1);color:var(--on);text-align:center;font-size:.82rem;padding:7px 16px;font-weight:600}
nav{position:sticky;top:0;z-index:50;background:var(--navbg);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;justify-content:space-between;height:70px;gap:16px}
.logo{display:flex;align-items:center;gap:10px;min-width:0}
.logo-mark{font-family:var(--disp);font-weight:var(--dw);font-size:1.6rem;line-height:1;color:var(--a1);letter-spacing:-.01em;white-space:nowrap}
.logo-sub{font-size:.62rem;letter-spacing:.2em;color:var(--muted);text-transform:uppercase;line-height:1.25;font-weight:700;border-left:2px solid var(--a2);padding-left:10px}
.nav-links{display:flex;gap:28px;font-weight:500;font-size:.95rem;color:var(--muted)}
.nav-links a:hover{color:var(--text)}
.nav-cta{padding:10px 20px;font-size:.9rem;white-space:nowrap}
.burger{display:none;background:none;border:0;color:var(--text);font-size:1.6rem;cursor:pointer}
.hero{position:relative;padding:100px 0 90px;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;background:radial-gradient(600px 400px at 85% 20%,var(--glow1),transparent 60%),radial-gradient(700px 500px at 0% 100%,var(--glow2),transparent 60%);pointer-events:none}
.hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:60px;align-items:center;position:relative}
.hero h1{font-size:clamp(2.5rem,5.6vw,4.4rem)}
.hl{background:linear-gradient(90deg,var(--a1),var(--a2));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p.lead{font-size:1.15rem;color:var(--muted);margin:24px 0 34px;max-width:560px}
.hero-ctas{display:flex;gap:14px;flex-wrap:wrap}
.badges{display:flex;gap:10px 22px;margin-top:38px;flex-wrap:wrap}
.badge{display:flex;align-items:center;gap:8px;font-size:.88rem;color:var(--muted);font-weight:500}
.badge i{width:8px;height:8px;border-radius:50%;background:var(--a2);box-shadow:0 0 10px var(--a2)}
.sweep-card{position:relative;aspect-ratio:1/1;border-radius:24px;overflow:hidden;border:1px solid var(--line);animation:clean 6s ease-in-out infinite}
.sweep-card .s-after,.sweep-card .s-before{position:absolute;inset:0}
.sweep-card .s-after{background:var(--after)}
.sweep-card .s-before{background:var(--before);clip-path:inset(0 0 0 var(--clean,0%))}
.sweep-card .beam{position:absolute;top:-10%;bottom:-10%;width:4px;left:var(--clean,0%);background:linear-gradient(transparent,#fff 20%,var(--a2) 50%,#fff 80%,transparent);box-shadow:0 0 18px 6px var(--a2)}
@property --clean{syntax:'<percentage>';inherits:true;initial-value:0%}
@keyframes clean{0%{--clean:0%}45%{--clean:100%}55%{--clean:100%}100%{--clean:0%}}
.tag{position:absolute;bottom:16px;padding:6px 12px;border-radius:999px;font-size:.75rem;font-weight:700;background:rgba(0,0,0,.6);color:#fff}
.tag.l{left:16px}.tag.r{right:16px}
.icon-card{position:relative;aspect-ratio:1/1;border-radius:24px;border:1px solid var(--line);background:radial-gradient(circle at 50% 45%,var(--glow1),transparent 65%),var(--card);display:grid;place-items:center;overflow:hidden}
.ring{position:absolute;border-radius:50%;border:1.5px dashed var(--line)}
.ring.r1{width:62%;aspect-ratio:1;animation:spin 40s linear infinite}
.ring.r2{width:86%;aspect-ratio:1;animation:spin 60s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
.big-ico{width:44%;aspect-ratio:1;border-radius:28%;display:grid;place-items:center;background:linear-gradient(135deg,var(--a1),var(--a2));box-shadow:0 30px 60px -20px var(--a1)}
.big-ico svg{width:52%;height:52%;stroke:var(--on);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.ftag{position:absolute;padding:8px 14px;border-radius:999px;background:var(--bg2);border:1px solid var(--line);font-weight:700;font-size:.82rem;box-shadow:0 10px 24px -12px rgba(0,0,0,.5);animation:bob 5s ease-in-out infinite;max-width:46%;text-align:center}
.ftag.f0{top:12%;left:8%}.ftag.f1{top:20%;right:6%;animation-delay:-1.6s}.ftag.f2{bottom:12%;left:22%;animation-delay:-3.2s}
@keyframes bob{50%{transform:translateY(-8px)}}
section{padding:96px 0}
.sec-head{max-width:720px;margin-bottom:52px}
.sec-head.center{margin-left:auto;margin-right:auto;text-align:center}
.sec-head h2{font-size:clamp(2rem,4vw,3rem)}
.sec-head p{color:var(--muted);font-size:1.08rem;margin-top:16px}
.alt{background:var(--bg2);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.svc-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.svc-grid.four{grid-template-columns:repeat(2,1fr)}
.svc{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:30px;transition:transform .25s,border-color .25s}
.svc:hover{transform:translateY(-4px);border-color:var(--a1)}
.ico{width:50px;height:50px;border-radius:12px;display:grid;place-items:center;background:var(--tint);margin-bottom:20px}
.ico svg{width:26px;height:26px;stroke:var(--a1);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.svc h3{font-size:1.18rem;margin-bottom:10px;font-family:Inter,sans-serif;font-weight:700}
.svc p{color:var(--muted);font-size:.96rem}
.ba{position:relative;max-width:900px;margin:0 auto;aspect-ratio:16/9;border-radius:20px;overflow:hidden;border:1px solid var(--line);user-select:none;touch-action:pan-y}
.ba .layer{position:absolute;inset:0}
.ba .after{background:var(--after)}
.ba .before{background:var(--before);clip-path:inset(0 calc(100% - var(--pos,50%)) 0 0)}
.lbl{position:absolute;top:18px;padding:7px 14px;border-radius:999px;font-weight:700;font-size:.8rem;background:rgba(0,0,0,.65);color:#fff}
.lbl.b{left:18px}.lbl.a{right:18px}
.handle{position:absolute;top:0;bottom:0;left:var(--pos,50%);width:3px;transform:translateX(-50%);background:var(--a2);box-shadow:0 0 20px 4px var(--a2)}
.handle::after{content:"\\27F7";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:46px;height:46px;border-radius:50%;background:#fff;color:#111;display:grid;place-items:center;font-weight:700;font-size:1.2rem;box-shadow:0 6px 20px rgba(0,0,0,.4)}
.ba input{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:ew-resize}
.ba-note{text-align:center;color:var(--muted);font-size:.88rem;margin-top:16px}
.opts{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:22px}
.opt{font:inherit;font-weight:600;font-size:.92rem;padding:10px 18px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--text);cursor:pointer}
.opt.on,.pick[aria-pressed="true"]{background:linear-gradient(135deg,var(--a1),var(--a2));color:var(--on);border-color:transparent}
.loadbox,.roombox,.swbox,.flakebox,.builder{max-width:820px;margin:0 auto;background:var(--card);border:1px solid var(--line);border-radius:20px;padding:28px}
.truck .t-bed{fill:var(--line)}.truck .t-in{fill:var(--bg)}.truck .t-fill{fill:var(--a1);transition:width .4s ease}
.truck .t-cab{fill:var(--a2)}.truck .t-win{fill:var(--bg2)}.truck .t-wh{fill:var(--text)}.truck .t-hub{fill:var(--muted)}
.check{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:24px}
.check.hide{display:none}
.check label{display:flex;gap:10px;align-items:center;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:var(--bg);font-weight:500;cursor:pointer}
.check input{accent-color:var(--a1);width:18px;height:18px}
.housev .h-ground{fill:var(--line)}.housev .h-roof{fill:none;stroke:var(--text);stroke-width:10;stroke-linejoin:round}
.housev .h-door{fill:var(--a1)}.housev .h-win{fill:var(--bg2);stroke:var(--text);stroke-width:4}.housev .h-mull{stroke:var(--text);stroke-width:3}
#wall{transition:fill .35s}
.sws{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:22px}
.sw{width:44px;height:44px;border-radius:50%;background:var(--c);border:3px solid var(--card);box-shadow:0 0 0 1px var(--line);cursor:pointer}
.sw.on{box-shadow:0 0 0 3px var(--a1)}
#floor{width:100%;height:auto;border-radius:14px;border:1px solid var(--line)}
.picks{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.pick{font:inherit;font-weight:600;padding:12px 18px;border-radius:999px;border:1px solid var(--line);background:var(--bg);color:var(--text);cursor:pointer}
.menu{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.mi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:24px;border-top:4px solid var(--a1)}
.mi h3{font-size:1.25rem;margin-bottom:6px}
.mi p{color:var(--muted);font-size:.95rem}
.vs-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px}
.vs-grid>*{min-width:0}
.vs-card{position:relative;border-radius:20px;padding:30px;border:1px solid var(--line);background:var(--card)}
.vs-card.today{background:var(--bg);border-style:dashed}
.vs-card.next{border:2px solid var(--a1);box-shadow:0 24px 50px -30px var(--a1)}
.vs-tag{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;padding:5px 12px;border-radius:999px;background:var(--line);color:var(--text);margin-bottom:12px}
.vs-card.next .vs-tag{background:linear-gradient(135deg,var(--a1),var(--a2));color:var(--on)}
.vs-card h3{font-size:1.5rem;margin-bottom:18px}
.vs-list{list-style:none;display:grid;gap:16px}
.vs-list li{display:flex;gap:12px;align-items:flex-start}
.vs-list b{display:block;font-size:1rem}
.vs-list span:not(.yes):not(.no){color:var(--muted);font-size:.92rem;overflow-wrap:anywhere}
.yes,.no{flex:none;width:26px;height:26px;border-radius:50%;display:inline-grid;place-items:center;font-weight:800;font-size:.85rem}
.yes{background:var(--tint);color:var(--a1)}
.no{background:rgba(220,60,60,.14);color:#d64545}
.part{color:var(--muted);font-size:.85rem;font-weight:600}
.vs-scroll{overflow-x:auto;border-radius:16px;border:1px solid var(--line)}
.vs-table{width:100%;border-collapse:collapse;background:var(--card);min-width:520px}
.vs-table th,.vs-table td{padding:14px 18px;text-align:left;border-bottom:1px solid var(--line);font-size:.95rem}
.vs-table th{font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.vs-table td:nth-child(n+2),.vs-table th:nth-child(n+2){text-align:center;width:24%}
.vs-table td .yes,.vs-table td .no{margin:0 auto}
.vs-table tr:last-child td{border-bottom:0}
.vs-table .sm{display:none}
.about-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:50px;align-items:start}
.about-grid p{color:var(--muted);font-size:1.06rem;margin-bottom:16px}
.facts{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:26px;display:grid;gap:18px}
.fact{display:flex;gap:14px;align-items:flex-start}
.fact .ico{margin:0;flex:none;width:44px;height:44px}
.fact b{display:block}.fact span{color:var(--muted);font-size:.92rem}
.chips{display:flex;flex-wrap:wrap;gap:12px}
.chip{padding:12px 20px;border:1px solid var(--line);border-radius:999px;background:var(--card);font-weight:600;font-size:.95rem}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;counter-reset:s}
.step{position:relative;padding:28px;border-radius:16px;background:var(--card);border:1px solid var(--line)}
.step::before{counter-increment:s;content:"0" counter(s);font-family:var(--disp);font-weight:var(--dw);font-size:2.6rem;color:transparent;-webkit-text-stroke:1.5px var(--a1);display:block;margin-bottom:12px}
.step h3{font-family:Inter,sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:6px}
.step p{color:var(--muted);font-size:.93rem}
.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:50px;align-items:start}
.contact-info h2{font-size:clamp(2rem,4vw,3rem)}
.contact-info>p{color:var(--muted);margin:18px 0 30px;font-size:1.06rem}
.ci-row{display:flex;gap:14px;align-items:center;margin-bottom:18px;font-weight:600;word-break:break-word}
.ci-row .ico{margin:0;flex:none;width:44px;height:44px;background:var(--card);border:1px solid var(--line)}
.ci-row svg{width:20px;height:20px}
.ci-row small{display:block;color:var(--muted);font-weight:500;font-size:.82rem}
form{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:32px;display:grid;gap:16px}
label.f{font-size:.85rem;font-weight:600;color:var(--muted);display:grid;gap:6px}
.f input,.f select,.f textarea{font:inherit;color:var(--text);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:13px 14px;width:100%}
.f input:focus,.f select:focus,.f textarea:focus{outline:none;border-color:var(--a1);box-shadow:0 0 0 3px var(--tint)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.thanks{display:none;text-align:center;padding:30px 0}
.thanks h3{font-size:1.6rem;margin-bottom:8px}
.callbar{display:none}
footer{border-top:1px solid var(--line);padding:40px 0;color:var(--muted);font-size:.88rem}
footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;align-items:center}
.reveal{opacity:0;transform:translateY(24px);transition:opacity .7s,transform .7s}
.reveal.in{opacity:1;transform:none}
:focus-visible{outline:2px solid var(--a1);outline-offset:3px}
@media (max-width:960px){
  .hero-grid,.contact-grid,.about-grid,.vs-grid{grid-template-columns:1fr}
  .svc-grid,.menu{grid-template-columns:1fr 1fr}
  .steps{grid-template-columns:1fr 1fr}
  .nav-links{display:none;position:absolute;top:70px;left:0;right:0;flex-direction:column;gap:0;background:var(--bg2);border-bottom:1px solid var(--line)}
  .nav-links.open{display:flex}
  .nav-links a{padding:16px 20px;border-top:1px solid var(--line)}
  .burger{display:block}
  .nav-cta{display:none}
  .hero-visual{max-width:460px}
}
@media (max-width:600px){
  .wrap{padding:0 16px}
  section{padding:68px 0}
  .hero{padding:64px 0 60px}
  .svc-grid,.svc-grid.four,.steps,.row2,.menu,.check,.vs-grid{grid-template-columns:1fr}
  .logo-sub{display:none}
  .vs-table{min-width:0}
  .vs-table th,.vs-table td{padding:11px 8px;font-size:.84rem}
  .vs-table td:nth-child(n+2),.vs-table th:nth-child(n+2){width:22%}
  .vs-table .lg{display:none}.vs-table .sm{display:inline}
  .part{font-size:.72rem}
  .vs-card{padding:24px 20px}
  .callbar{display:flex;position:fixed;left:12px;right:12px;bottom:12px;z-index:60;justify-content:center;padding:15px;border-radius:999px;font-weight:700;background:linear-gradient(135deg,var(--a1),var(--a2));color:var(--on);box-shadow:0 12px 30px -10px rgba(0,0,0,.6)}
  footer{padding-bottom:96px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.reveal{opacity:1;transform:none}}
"""

JS = """
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
$('#burger').onclick=()=>$('#navLinks').classList.toggle('open');
$$('#navLinks a').forEach(a=>a.onclick=()=>$('#navLinks').classList.remove('open'));
const det=$('#details');let extra='';
function note(t){extra=t;if(det&&!det.dataset.touched)det.value=t}
if(det)det.addEventListener('input',()=>det.dataset.touched=1);
const ba=$('#ba'),r=$('#baRange');if(r)r.addEventListener('input',()=>ba.style.setProperty('--pos',r.value+'%'));
$$('#loadOpts .opt').forEach(b=>b.onclick=()=>{$$('#loadOpts .opt').forEach(x=>x.classList.remove('on'));b.classList.add('on');
  $('#fill').setAttribute('width',Math.round(242*b.dataset.fill/100));$('#loadNote').textContent=b.dataset.name+' selected. Added to your quote request below.';note('Load size: '+b.dataset.name+'. ')});
$$('#roomTabs .opt').forEach(b=>b.onclick=()=>{$$('#roomTabs .opt').forEach(x=>x.classList.remove('on'));b.classList.add('on');
  $$('.check').forEach(l=>l.classList.toggle('hide',l.dataset.list!==b.dataset.room))});
$$('.sw').forEach(b=>b.onclick=()=>{$$('.sw').forEach(x=>x.classList.remove('on'));b.classList.add('on');$('#wall').style.fill=b.dataset.c;$('#swName').textContent=b.dataset.name;note('Color I like: '+b.dataset.name+'. ')});
const cv=$('#floor');function floor(cols){const c=cv.getContext('2d'),w=cv.width,h=cv.height;c.fillStyle=cols[0];c.fillRect(0,0,w,h);
  let s=7;const rnd=()=>(s=(s*16807)%2147483647)/2147483647;for(let i=0;i<5200;i++){c.fillStyle=cols[i%cols.length];c.globalAlpha=.85;
  const x=rnd()*w,y=rnd()*h,z=2+rnd()*5;c.beginPath();c.moveTo(x,y);c.lineTo(x+z,y+rnd()*3);c.lineTo(x+rnd()*3,y+z);c.fill()}
  c.globalAlpha=1;const g=c.createLinearGradient(0,0,w,h);g.addColorStop(0,'rgba(255,255,255,.22)');g.addColorStop(.4,'rgba(255,255,255,0)');c.fillStyle=g;c.fillRect(0,0,w,h)}
if(cv){floor($('#flakeOpts .opt').dataset.c.split(','));$$('#flakeOpts .opt').forEach(b=>b.onclick=()=>{$$('#flakeOpts .opt').forEach(x=>x.classList.remove('on'));b.classList.add('on');floor(b.dataset.c.split(','));note('Flake blend: '+b.dataset.name+'. ')})}
$$('.pick').forEach(b=>b.onclick=()=>{b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true');
  const on=[...$$('.pick')].filter(x=>x.getAttribute('aria-pressed')==='true').map(x=>x.textContent);
  $('#pickNote').textContent=on.length?on.length+' selected. Added to your quote request below.':'Nothing selected yet.';note(on.length?'I need: '+on.join(', ')+'. ':'')});
function submitQuote(e){e.preventDefault();$('#formFields').style.display='none';$('#thanks').style.display='block';return false}
const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12});
$$('.reveal').forEach(el=>io.observe(el));
"""


def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def tel(p):
    d = re.sub(r"\D", "", p)
    return "+1" + d[-10:] if len(d) >= 10 else d


def page(b):
    ind = IND[b["ind"]]
    key = b["slug"]
    pal = PALETTES[b.get("pal") or pick(ind["pals"], key, "p")]
    font = FONTS[b.get("font") or pick(ind["fonts"], key, "f")]
    bg, bg2, card, line, text, muted, a1, a2, mode = pal
    dark = mode == "dark"
    on = "#0b0f14" if lum(a1) > 0.28 else "#ffffff"
    navbg = (bg + "d1") if len(bg) == 7 else bg
    glow1 = a1 + ("2e" if dark else "1f")
    glow2 = a2 + ("26" if dark else "1a")
    tint = a1 + ("26" if dark else "1a")
    name = b["name"]
    logo = b.get("logo") or [name.split()[0].upper(), " ".join(name.split()[1:]) or ind["label"]]
    tex = BA[b.get("ba", ind.get("ba", "concrete"))]
    mod_html, mod_id, mod_label = MODULES[b.get("module", ind["module"])](b, ind)
    presence_html = presence_section(b, ind, b.get("module", ind["module"]))
    cta = b.get("cta", ind["cta"])
    phone = b.get("phone", "")
    primary_href = f"tel:{tel(phone)}" if phone else "#contact"
    primary_txt = f"Call {phone}" if phone else cta + " →"

    svcs = "".join(f'''<div class="svc reveal"><div class="ico">{svg(s[2] if len(s) > 2 else icon_for(s[0]))}</div><h3>{e(s[0])}</h3><p>{e(s[1])}</p></div>''' for s in b["services"])
    badges = "".join(f'<span class="badge"><i></i>{e(x)}</span>' for x in b["badges"])
    chips = "".join(f'<span class="chip">{e(x)}</span>' for x in b.get("chips", []))
    steps = "".join(f'<div class="step reveal"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in b.get("steps", ind["steps"]))
    about = "".join(f"<p>{e(p)}</p>" for p in b["about"])

    facts = [("pin", b.get("where", f'{b["city"]}, {b["st"]}'), b.get("area", ""))]
    if b.get("hours"):
        facts.append(("clock", "Hours", b["hours"]))
    for f in b.get("facts", []):
        facts.append(tuple(f))
    facts_html = "".join(f'<div class="fact"><div class="ico">{svg(i)}</div><div><b>{e(t)}</b>{f"<span>{e(s)}</span>" if s else ""}</div></div>' for i, t, s in facts)

    rows = []
    if phone:
        rows.append(f'<a class="ci-row" href="tel:{tel(phone)}"><span class="ico">{svg("phone")}</span><span>{e(phone)}<small>Call or text</small></span></a>')
    if b.get("email"):
        rows.append(f'<a class="ci-row" href="mailto:{e(b["email"])}"><span class="ico">{svg("mail")}</span><span>{e(b["email"])}<small>Email us</small></span></a>')
    if b.get("fb"):
        rows.append(f'<a class="ci-row" href="{e(b["fb"])}" target="_blank" rel="noopener"><span class="ico">{svg("fb")}</span><span>Facebook<small>Message us or see recent work</small></span></a>')
    if b.get("ig"):
        rows.append(f'<a class="ci-row" href="https://www.instagram.com/{e(b["ig"])}/" target="_blank" rel="noopener"><span class="ico">{svg("ig")}</span><span>@{e(b["ig"])}<small>Follow on Instagram</small></span></a>')
    rows.append(f'<div class="ci-row"><span class="ico">{svg("pin")}</span><span>{e(b.get("where", b["city"] + ", " + b["st"]))}<small>{e(b.get("area", ""))}</small></span></div>')
    opts = "".join(f"<option>{e(s[0])}</option>" for s in b["services"]) + "<option>Something else</option>"
    src_name = b.get("src_short", "the business's public Facebook page")
    social = b.get("fb") or (f'https://www.instagram.com/{b["ig"]}/' if b.get("ig") else "")
    nav_links = [("online", "Online Today"), ("services", "Services"), (mod_id, mod_label), ("about", "About"), ("process", "How It Works"), ("contact", "Contact")]
    nav = "".join(f'<a href="#{i}">{t}</a>' for i, t in nav_links)
    desc = b.get("meta", b["lead"])[:155]
    callbar = f'<a class="callbar" href="tel:{tel(phone)}">Call {e(phone)}</a>' if phone else f'<a class="callbar" href="#contact">{e(cta)}</a>'
    ph_placeholder = phone or "(555) 555-0100"

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(name)}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{font[1]}&display=swap" rel="stylesheet">
<style>
:root{{--bg:{bg};--bg2:{bg2};--card:{card};--line:{line};--text:{text};--muted:{muted};--a1:{a1};--a2:{a2};--on:{on};
--navbg:{navbg};--glow1:{glow1};--glow2:{glow2};--tint:{tint};--disp:{font[0]};--dw:{font[2]};color-scheme:{mode}}}
.ba,.sweep-card{{--before:{tex[0]};--after:{tex[1]}}}
{CSS}
</style>
</head>
<body>
<div class="demo">Website concept preview, prepared for {e(name)}</div>
<nav>
  <div class="wrap">
    <a href="#top" class="logo" aria-label="{e(name)} home"><span class="logo-mark">{e(logo[0])}</span><span class="logo-sub">{"<br>".join(e(x) for x in logo[1].split("|"))}</span></a>
    <div class="nav-links" id="navLinks">{nav}</div>
    <a href="#contact" class="btn btn-primary nav-cta">{e(cta)}</a>
    <button class="burger" id="burger" aria-label="Menu">&#9776;</button>
  </div>
</nav>
<header class="hero" id="top">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">{e(b.get("eyebrow", b["city"] + ", " + b["st"] + " · " + ind["label"]))}</span>
      <h1>{hl(b["h1"])}</h1>
      <p class="lead">{e(b["lead"])}</p>
      <div class="hero-ctas"><a href="{primary_href}" class="btn btn-primary">{e(primary_txt)}</a><a href="#{mod_id}" class="btn btn-ghost">{e(b.get("cta2", "See " + mod_label))}</a></div>
      <div class="badges">{badges}</div>
    </div>
    <div class="hero-visual">{hero_visual(b, ind)}</div>
  </div>
</header>
{presence_html}
<section id="services">
  <div class="wrap">
    <div class="sec-head reveal"><span class="eyebrow">{e(b.get("svc_eyebrow", "Services"))}</span><h2>{e(b.get("svc_title", "What we do"))}</h2><p>{e(b.get("svc_text", ""))}</p></div>
    <div class="svc-grid{" four" if len(b["services"]) == 4 else ""}">{svcs}</div>
  </div>
</section>
{mod_html}
<section id="about">
  <div class="wrap about-grid">
    <div class="reveal"><span class="eyebrow">About</span><h2 style="font-size:clamp(2rem,4vw,3rem);margin-bottom:22px">{e(b.get("about_title", "About " + name))}</h2>{about}</div>
    <div class="facts reveal">{facts_html}</div>
  </div>
</section>
{f"""<section id="area" class="alt"><div class="wrap"><div class="sec-head reveal"><span class="eyebrow">{e(b.get("chips_title", ind["chips_title"]))}</span><h2>{e(b.get("chips_h2", "Big jobs, small jobs, and everything in between."))}</h2></div><div class="chips reveal">{chips}</div></div></section>""" if chips else ""}
<section id="process">
  <div class="wrap">
    <div class="sec-head reveal"><span class="eyebrow">How It Works</span><h2>{e(b.get("steps_title", "Simple from first message to finished job."))}</h2></div>
    <div class="steps">{steps}</div>
  </div>
</section>
<section id="contact" class="alt">
  <div class="wrap contact-grid">
    <div class="contact-info reveal">
      <span class="eyebrow">Contact</span><h2>{e(b.get("contact_title", "Let's talk about your project."))}</h2>
      <p>{e(b.get("contact_text", "Call, message or send a request below. Photos help with a faster quote."))}</p>
      {"".join(rows)}
    </div>
    <form id="quote" class="reveal" onsubmit="return submitQuote(event)">
      <div id="formFields" style="display:grid;gap:16px">
        <div class="row2"><label class="f">Name<input required placeholder="Your name"></label><label class="f">Phone<input type="tel" placeholder="{e(ph_placeholder)}"></label></div>
        <label class="f">Email<input type="email" placeholder="you@email.com"></label>
        <label class="f">Service needed<select>{opts}</select></label>
        <label class="f">Details<textarea id="details" rows="4" placeholder="{e(b.get("form_hint", "Tell us about the job, the size and your address"))}"></textarea></label>
        <button class="btn btn-primary" type="submit" style="justify-content:center">{e(b.get("submit", "Send My Request"))}</button>
      </div>
      <div class="thanks" id="thanks"><h3>Thanks!</h3><p style="color:var(--muted)">{e(name)} will get back to you soon.<br><small>(Demo form: nothing was sent.)</small></p></div>
    </form>
  </div>
</section>
<footer>
  <div class="wrap">
    <a href="#top" class="logo"><span class="logo-mark" style="font-size:1.25rem">{e(logo[0])}</span></a>
    <span>Demo site prepared by Lake Houston Web Co. Not an official site. Facts from {e(src_name)} as of {e(b.get("viewed", "Nov 2026"))}.</span>
    {f'<a href="{e(social)}" target="_blank" rel="noopener">Facebook ↗</a>' if b.get("fb") else (f'<a href="{e(social)}" target="_blank" rel="noopener">Instagram ↗</a>' if social else "")}
  </div>
</footer>
{callbar}
<script>{JS}</script>
</body>
</html>
'''


def sources(b):
    lines = [f'Facts used on this demo come from {b.get("src_short", "the business public Facebook page")}, viewed {b.get("viewed", "Nov 2026")}:']
    for s in b.get("sources", []):
        lines.append("- " + s)
    lines += ["", "Before/after and hero images are CSS illustrations, not photos of this business's work.",
              "No reviews, prices, awards or years in business were invented."]
    return "\n".join(lines) + "\n"


def load(slugs):
    files = [s if s.endswith(".json") else os.path.join(DATA, s + ".json") for s in slugs] if slugs else sorted(glob.glob(os.path.join(DATA, "*.json")))
    out = []
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        out.extend(d if isinstance(d, list) else [d])
    return out


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    for b in load(sys.argv[2:]):
        b.setdefault("slug", slugify(b["name"] + "-" + b["city"]))
        d = os.path.join(root, b["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(b))
        open(os.path.join(d, "SOURCES.txt"), "w", encoding="utf-8").write(sources(b))
        print("built", b["slug"])


if __name__ == "__main__":
    main()
