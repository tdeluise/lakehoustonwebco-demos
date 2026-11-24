#!/usr/bin/env python3
"""Turn verified lead rows into signature-demo JSON. Only listing facts are used:
name, category, city, address, phone. No ratings, prices, years or reviews are invented."""
import json, re, os, sys
from build import build

def slug(s): return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')
def nice(s):
    s = s.strip()
    if s.isupper() or s.islower(): s = re.sub(r"\b([a-z])", lambda m: m.group(1).upper(), s.lower()).replace("'S ", "'s ")
    return s

# key: (match regex on category, photo, label, h1, services[4], palette(a1,a2,mode,bg), font, food?)
G = [
 (r'body shop|collision', 'autobody', 'Auto Body Shop', 'Collision repair that *looks factory-new.*', [['Collision Repair','Dents, panels and frames.'],['Paint & Refinish','Color-matched finish.'],['Insurance Claims','Help with the paperwork.'],['Free Estimates','Bring it by or call.']]),
 (r'detail', 'detailing', 'Auto Detailing', 'Showroom shine, *inside and out.*', [['Exterior Detail','Wash, clay and wax.'],['Interior Detail','Seats, carpet, dash.'],['Ceramic & Paint','Protection that lasts.'],['Packages','Ask what fits your car.']]),
 (r'tint', 'tint', 'Window Tinting', 'Cooler rides, *cleaner looks.*', [['Window Tint','Cars, trucks, SUVs.'],['Heat Rejection','Beat the Texas sun.'],['Removal','Old tint off clean.'],['Quotes','Call for a price.']]),
 (r'tire', 'tires', 'Tire Shop', 'The right tires, *at a fair price.*', [['New Tires','Most sizes.'],['Used Tires','Good tread, good price.'],['Mount & Balance','Done right.'],['Flat Repair','Back on the road.']]),
 (r'towing', 'towing', 'Towing Service', 'Stuck? *Help is a call away.*', [['Towing','Local and long distance.'],['Roadside Help','Jumps, lockouts, tires.'],['Flatbed','Safe transport.'],['Call Anytime','Ask about availability.']]),
 (r'motorcycle|truck repair|automotive|auto|mechanic|oil', 'autorepair2', 'Auto Repair', 'Honest auto repair *you can count on.*', [['Diagnostics','Find the real problem.'],['Brakes','Pads, rotors, fluid.'],['Engine & A/C','Repairs and service.'],['Maintenance','Oil, belts, filters.']]),
 (r'landscap|gardener|lawn', 'landscaping', 'Landscaping', 'A yard you’re *proud to come home to.*', [['Lawn Care','Mow, edge, blow.'],['Landscaping','Beds, plants, mulch.'],['Cleanups','Leaves and limbs.'],['Free Quotes','Call to set a visit.']]),
 (r'tree', 'tree', 'Tree Service', 'Trimming, removal *and cleanup.*', [['Tree Trimming','Shape and clear.'],['Tree Removal','Safe takedowns.'],['Stump Grinding','Clean finish.'],['Storm Cleanup','Fast response.']]),
 (r'groom', 'grooming', 'Pet Grooming', 'Clean, fluffy *and happy.*', [['Bath & Brush','Fresh and soft.'],['Full Groom','Cut and style.'],['Nails & Ears','The little things.'],['Book a Visit','Call to schedule.']]),
 (r'pet store|pet supply', 'petstore', 'Pet Store', 'Everything your pet *needs.*', [['Food & Treats','The good stuff.'],['Toys & Gear','Leashes, beds, toys.'],['Supplies','Everyday basics.'],['Ask Us','Friendly help.']]),
 (r'horse|equine', 'horse', 'Horse Boarding', 'Good care *for your horse.*', [['Boarding','Stalls and turnout.'],['Feeding','Daily care.'],['Facilities','Ask for a tour.'],['Call Us','Check availability.']]),
 (r'vet|animal hosp', 'vet', 'Veterinarian', 'Caring for pets *like family.*', [['Wellness Exams','Checkups and vaccines.'],['Sick Visits','When they’re not right.'],['Dental','Healthy smiles.'],['Call to Book','Schedule a visit.']]),
 (r'pet|animal|dog|kennel|boarding', 'grooming', 'Pet Care', 'Happy pets, *happy owners.*', [['Pet Care','Ask what we offer.'],['Boarding & Sitting','When you’re away.'],['Training','Good habits.'],['Call Us','Check availability.']]),
 (r'bakery|cake|dessert|cupcake', 'bakery', 'Bakery', 'Baked fresh, *made to celebrate.*', [['Custom Cakes','Birthdays, weddings, more.'],['Cupcakes & Cookies','By the dozen.'],['Fresh Bakes','Daily favorites.'],['Order Ahead','Call to order.']], 'cake'),
 (r'donut|kolache', 'donuts', 'Donut Shop', 'Fresh donuts *every morning.*', [['Donuts','Glazed, filled, cake.'],['Kolaches','Sausage and cheese.'],['By the Dozen','For the office.'],['Coffee','Hot and ready.']], 'cake'),
 (r'ice cream|frozen|paleta|gelato', 'icecream', 'Ice Cream Shop', 'Something sweet, *any time.*', [['Scoops','Cups and cones.'],['Shakes','Thick and cold.'],['Toppings','Pile it on.'],['Parties','Ask about orders.']], 'food'),
 (r'barbecue|bbq|smokehouse', 'bbq', 'Barbecue', 'Low and slow, *smoked right.*', [['Brisket','Smoked low and slow.'],['Ribs','Fall-off tender.'],['Sausage','Snappy and smoky.'],['Catering','Feed the whole crew.']], 'food'),
 (r'food truck|taco', 'taco_trailer', 'Food Truck', 'Made fresh *from the window.*', [['Tacos','Street-style.'],['Plates','Hearty and filling.'],['Daily Specials','Ask what’s cooking.'],['To-Go','Grab it and go.']], 'food'),
 (r'mexican|tex|latin', 'tacos', 'Mexican Restaurant', 'Real Mexican food, *made fresh.*', [['Tacos','Street-style.'],['Enchiladas','Saucy and cheesy.'],['Breakfast','Breakfast tacos.'],['To-Go','Call ahead.']], 'food'),
 (r'cater', 'catering', 'Catering', 'Food your guests *will remember.*', [['Events','Parties and weddings.'],['Corporate','Office lunches.'],['Custom Menus','Built around you.'],['Get a Quote','Tell us the date.']], 'food'),
 (r'coffee|cafe|tea|boba|bubble', 'coffee', 'Coffee Shop', 'Your new *favorite cup.*', [['Coffee','Hot and iced.'],['Espresso Drinks','Lattes and more.'],['Bites','Pastries and snacks.'],['Grab & Go','Quick stop.']], 'food'),
 (r'juice|smoothie', 'juice', 'Juice Bar', 'Fresh, cold *and good for you.*', [['Juices','Fresh pressed.'],['Smoothies','Blended to order.'],['Bowls','Topped fresh.'],['Grab & Go','Quick stop.']], 'food'),
 (r'burger|grill|bar ', 'burgers', 'Bar & Grill', 'Good food, *cold drinks.*', [['Burgers','Hot off the grill.'],['Sides','Fries and rings.'],['Drinks','Cold and ready.'],['Hangout','Bring your friends.']], 'food'),
 (r'restaurant|diner|deli|food|sandwich|pizza|steak|brunch|kitchen', 'restaurant', 'Restaurant', 'Hearty food, *made with care.*', [['Lunch','Daily favorites.'],['Dinner','Plates and specials.'],['To-Go','Call ahead.'],['Catering','Ask about events.']], 'food'),
 (r'party|event plan|wedding|rental|decor|balloon', 'party', 'Event Planning', 'Events people *talk about after.*', [['Event Planning','Start to finish.'],['Decor & Setup','Balloons, backdrops.'],['Parties','Birthdays and more.'],['Get a Quote','Tell us the date.']]),
 (r'photo|video', 'photo', 'Photography', 'Moments worth *keeping forever.*', [['Portraits','Families and seniors.'],['Events','Weddings and parties.'],['Sessions','Indoor and outdoor.'],['Book a Date','Check availability.']]),
 (r'nail', 'nails', 'Nail Salon', 'Your nails, *your way.*', [['Manicures','Classic and gel.'],['Pedicures','Soak and polish.'],['Full Sets','Acrylic and dip.'],['Nail Art','Designs and details.']]),
 (r'barber', 'barber', 'Barbershop', 'Clean cuts, *sharp fades.*', [['Haircuts','Classic and modern.'],['Fades','Skin to taper.'],['Beard Trims','Line-ups and shaping.'],['Walk-ins','Call to check the wait.']]),
 (r'tattoo|pierc', 'tattoo', 'Tattoo Studio', 'Custom ink, *done right.*', [['Custom Tattoos','Your idea, drawn up.'],['Cover-ups','Make it new.'],['Piercing','Clean and safe.'],['Consults','Talk it through.']]),
 (r'massage|spa|skin|facial|tanning|makeup|lash|wax|brow', 'spa', 'Spa', 'Relax, reset, *feel like you.*', [['Treatments','Ask about the menu.'],['Skin & Body','Feel refreshed.'],['Packages','Treat yourself.'],['Book a Visit','Call to schedule.']]),
 (r'salon|hair|beauty|braid', 'hairsalon', 'Hair Salon', 'Hair that makes you *feel good.*', [['Cuts & Styles','For everyone.'],['Color','Highlights and more.'],['Treatments','Healthy hair.'],['Book a Visit','Call to schedule.']]),
 (r'plumb|septic', 'plumbing', 'Plumbing', 'Fast, clean *plumbing repairs.*', [['Repairs','Leaks and clogs.'],['Water Heaters','Repair and replace.'],['Drains','Cleared right.'],['Call Us','Get on the schedule.']]),
 (r'electric', 'electric', 'Electrician', 'Safe, reliable *electrical work.*', [['Repairs','Outlets, switches, breakers.'],['Panels','Upgrades and fixes.'],['Lighting','Indoor and outdoor.'],['Call Us','Get a quote.']]),
 (r'hvac|air cond|heating', 'hvac', 'Heating & Air', 'Cool summers, *warm winters.*', [['A/C Repair','Fast fixes.'],['Heating','Furnace and heat pumps.'],['Tune-Ups','Keep it running.'],['New Systems','Ask about options.']]),
 (r'roof|gutter', 'roofing', 'Roofing', 'A roof you *don’t think about.*', [['Roof Replacement','Done right.'],['Repairs','Leaks and storm damage.'],['Inspections','Know where you stand.'],['Gutters','Keep water moving.']]),
 (r'paint', 'paint', 'Painting', 'Clean walls, *sharp lines.*', [['Interior Painting','Rooms and trim.'],['Exterior Painting','Siding and doors.'],['Drywall Repair','Patch and texture.'],['Free Estimates','Call for a price.']]),
 (r'fence|gate|deck', 'fence', 'Fencing', 'Strong fences, *clean lines.*', [['Wood Fences','Privacy and style.'],['Gates','Built to swing right.'],['Repairs','Fix what’s leaning.'],['Free Quotes','Call for a price.']]),
 (r'garage door', 'garagedoor', 'Garage Doors', 'Garage doors that *just work.*', [['Repairs','Springs and openers.'],['New Doors','Install and replace.'],['Openers','Quiet and smart.'],['Call Us','Get on the schedule.']]),
 (r'pest|termite', 'pest', 'Pest Control', 'Bugs out, *peace of mind in.*', [['General Pest','Ants, roaches, spiders.'],['Termites','Inspection and treatment.'],['Rodents','Seal and remove.'],['Call Us','Set a visit.']]),
 (r'lock', 'locksmith', 'Locksmith', 'Locked out? *We’ll get you in.*', [['Lockouts','Home and car.'],['Rekeying','New keys, same locks.'],['Lock Install','Deadbolts and smart locks.'],['Call Us','Fast help.']]),
 (r'pool', 'pool', 'Pool Service', 'Clear water, *all season.*', [['Weekly Service','Clean and balanced.'],['Repairs','Pumps and filters.'],['Openings','Ready to swim.'],['Free Quotes','Call for a price.']]),
 (r'carpet clean|upholster', 'carpet', 'Carpet Cleaning', 'Carpets that *feel new again.*', [['Carpet Cleaning','Deep steam clean.'],['Upholstery','Sofas and chairs.'],['Pet Stains','Spots and odors.'],['Free Quotes','Call for a price.']]),
 (r'janitor|commercial clean', 'janitorial', 'Commercial Cleaning', 'A spotless space, *every time.*', [['Office Cleaning','Daily or weekly.'],['Floor Care','Strip and wax.'],['Deep Cleans','Top to bottom.'],['Get a Quote','Tell us the space.']]),
 (r'clean|maid', 'cleaning', 'Cleaning Service', 'Come home to *a clean house.*', [['House Cleaning','Weekly or one-time.'],['Deep Cleans','Top to bottom.'],['Move-Out','Leave it spotless.'],['Free Quotes','Call for a price.']]),
 (r'carpent|cabinet|remodel|contractor|construct|floor|mason|concrete|home improve|weld', 'carpenter', 'Contractor', 'Built right, *built to last.*', [['Custom Builds','Made to fit.'],['Repairs','Fix it right.'],['Remodels','Kitchens, baths, more.'],['Free Estimates','Call for a price.']]),
 (r'handyman', 'handyman', 'Handyman', 'Your to-do list, *done.*', [['Repairs','Doors, drywall, more.'],['Installs','Fixtures and shelves.'],['Small Projects','No job too small.'],['Free Quotes','Call for a price.']]),
 (r'martial|karate|jiu|taekwondo|boxing|mma', 'martial', 'Martial Arts', 'Strength, focus, *confidence.*', [['Kids Classes','Discipline and fun.'],['Adult Classes','All levels.'],['Self-Defense','Real skills.'],['Free Trial','Ask about a first class.']]),
 (r'dance|gymnast|cheer', 'dance', 'Dance Studio', 'Find your *rhythm here.*', [['Kids Classes','Ballet, jazz, hip-hop.'],['Teens & Adults','All levels.'],['Recitals','Show what you learned.'],['Enroll','Call to sign up.']]),
 (r'yoga|pilates', 'yoga', 'Yoga Studio', 'Breathe, move, *feel better.*', [['Classes','All levels.'],['Beginners','Start here.'],['Private Sessions','One-on-one.'],['First Class','Ask about trials.']]),
 (r'gym|fitness|train|crossfit', 'gym', 'Gym', 'Stronger starts *here.*', [['Memberships','Ask about options.'],['Training','Coaching that works.'],['Classes','Train together.'],['Free Visit','Come see it.']]),
 (r'jewel', 'jewelry', 'Jewelry Store', 'Jewelry for the *moments that matter.*', [['Engagement','Rings and bands.'],['Custom Design','Made for you.'],['Repairs','Sizing and fixes.'],['Cleaning','Make it shine.']]),
 (r'furniture|mattress', 'furniture', 'Furniture Store', 'Furniture that *feels like home.*', [['Living Room','Sofas and tables.'],['Bedroom','Beds and dressers.'],['Dining','Gather around.'],['Delivery','Ask about it.']]),
 (r'boutique|women|bridal|clothing|apparel|fashion|shoe|children', 'boutique', 'Boutique', 'Your new *favorite boutique.*', [['New Arrivals','Fresh every week.'],['Styles','Everyday to dressy.'],['Accessories','Finish the look.'],['Visit Us','Shop in store.']]),
 (r'laundr|dry clean|alteration|sewing', 'laundry', 'Laundry & Dry Cleaning', 'Clean, pressed *and ready.*', [['Wash & Fold','Drop it off.'],['Dry Cleaning','Pressed sharp.'],['Alterations','The perfect fit.'],['Pickup','Ask about it.']]),
]
FALLBACK = {
 'Home & trade services': ('handyman','Home Services','Local work, *done right.*',[['Services','Ask what we offer.'],['Repairs','Fix it right.'],['Projects','Big or small.'],['Free Quotes','Call for a price.']]),
 'Automotive': ('autorepair2','Auto Service','Car trouble? *We can help.*',[['Diagnostics','Find the problem.'],['Repairs','Fix it right.'],['Maintenance','Keep it running.'],['Call Us','Get a quote.']]),
 'Food & drink': ('restaurant','Restaurant','Good food, *made fresh.*',[['Menu','Daily favorites.'],['Specials','Ask what’s new.'],['To-Go','Call ahead.'],['Catering','Ask about events.']], 'food'),
 'Beauty & personal care': ('hairsalon','Beauty','Look good, *feel good.*',[['Services','Ask about the menu.'],['Treatments','Feel refreshed.'],['Packages','Treat yourself.'],['Book','Call to schedule.']]),
 'Pet services': ('grooming','Pet Care','Happy pets, *happy owners.*',[['Pet Care','Ask what we offer.'],['Grooming','Clean and fresh.'],['Boarding','When you’re away.'],['Call Us','Check availability.']]),
 'Events & creative services': ('party','Events','Events people *talk about after.*',[['Planning','Start to finish.'],['Setup','Decor and more.'],['Parties','All occasions.'],['Get a Quote','Tell us the date.']]),
 'Fitness & studios': ('fitness','Fitness','Stronger starts *here.*',[['Classes','All levels.'],['Training','Coaching that works.'],['Memberships','Ask about options.'],['Free Visit','Come see it.']]),
 'Local retail & repair': ('generic_shop','Local Shop','Your local shop, *right here.*',[['Shop','In-store selection.'],['Special Orders','Ask us.'],['Repairs','Ask about service.'],['Visit','Stop by.']]),
}
PAL = {'autobody':('#d62828','#f77f00','dark','#0e0e11'),'detailing':('#2563eb','#38bdf8','dark','#070b12'),'tint':('#64748b','#f59e0b','dark','#0b0c0f'),
 'tires':('#e11d48','#facc15','dark','#0d0d0f'),'towing':('#f59e0b','#ef4444','dark','#0d0d0f'),'autorepair2':('#dc2626','#fbbf24','dark','#0c0d10'),
 'landscaping':('#15803d','#a3e635','light','#f6faf3'),'tree':('#2f7d32','#c9a227','dark','#0b140c'),'grooming':('#0ea5a4','#f472b6','light','#f4fbfb'),
 'petstore':('#0ea5a4','#f59e0b','light','#f5fbfa'),'horse':('#8b5e34','#d4a373','light','#faf6f0'),'vet':('#0284c7','#22c55e','light','#f3f9fd'),
 'bakery':('#db2777','#f59e0b','light','#fff7f9'),'donuts':('#e85d75','#ffb703','light','#fff8f0'),'icecream':('#ec4899','#06b6d4','light','#fff6fb'),
 'bbq':('#b91c1c','#f59e0b','dark','#120b08'),'taco_trailer':('#ea580c','#facc15','dark','#120c07'),'tacos':('#16a34a','#ef4444','dark','#0c120c'),
 'catering':('#9a3412','#eab308','light','#fbf7f1'),'coffee':('#7c4a2d','#d4a373','light','#faf6f1'),'juice':('#16a34a','#f97316','light','#f6fbf3'),
 'burgers':('#c2410c','#facc15','dark','#100c09'),'restaurant':('#b45309','#dc2626','light','#fbf7f2'),'party':('#b8860b','#e8b4bc','light','#fdf9f5'),
 'photo':('#334155','#f59e0b','dark','#0b0d10'),'nails':('#c9a227','#e8b4bc','light','#fffaf7'),'barber':('#1e3a8a','#dc2626','dark','#0b0d14'),
 'tattoo':('#dc2626','#a3a3a3','dark','#0a0a0a'),'spa':('#8b7355','#c4b5a0','light','#faf7f3'),'hairsalon':('#9d4edd','#f4a261','light','#fbf7fd'),
 'plumbing':('#1d4ed8','#06b6d4','light','#f4f8fd'),'electric':('#ca8a04','#1e40af','dark','#0b0d12'),'hvac':('#0369a1','#f97316','light','#f3f8fc'),
 'roofing':('#9f1239','#64748b','light','#faf7f7'),'paint':('#1d4ed8','#f59e0b','light','#f7f9fc'),'fence':('#92400e','#65a30d','light','#faf7f1'),
 'garagedoor':('#334155','#0ea5e9','light','#f6f8fa'),'pest':('#15803d','#eab308','light','#f6faf4'),'locksmith':('#0f766e','#f59e0b','dark','#081110'),
 'pool':('#0284c7','#22d3ee','light','#f2f9fd'),'carpet':('#0d9488','#3b82f6','light','#f3fbfa'),'janitorial':('#1e40af','#10b981','light','#f5f7fc'),
 'cleaning':('#0891b2','#a3e635','light','#f3fbfc'),'carpenter':('#a16207','#475569','light','#faf8f3'),'handyman':('#ea580c','#334155','light','#fbf8f5'),
 'martial':('#b91c1c','#111827','dark','#0d0b0b'),'dance':('#be185d','#a78bfa','dark','#0f0a10'),'yoga':('#65a30d','#d97706','light','#f8faf3'),
 'gym':('#ef4444','#f59e0b','dark','#0b0b0d'),'fitness':('#f97316','#22c55e','dark','#0b0c0d'),'jewelry':('#b8860b','#6b7280','dark','#0c0b09'),
 'furniture':('#78350f','#a3a3a3','light','#faf7f2'),'boutique':('#be185d','#d4a373','light','#fdf8f8'),'laundry':('#0284c7','#a855f7','light','#f4f8fd'),
 'generic_shop':('#0f766e','#f59e0b','light','#f6faf8')}
FONT = {'food':'lobster','cake':'lobster'}

def make(r):
    cat = r['Category']; c = cat.lower()
    hit = None
    for g in G:
        if re.search(g[0], c): hit = g; break
    if hit: _, photo, label, h1, svc = hit[:5]; ind = hit[5] if len(hit) > 5 else 'service'
    else:
        fb = FALLBACK.get(r['Industry'], FALLBACK['Local retail & repair'])
        photo, label, h1, svc = fb[:4]; ind = fb[4] if len(fb) > 4 else 'service'
    name = nice(r['Business']); city = nice(r['City']); st = r['State']
    phone = r['Business Phone'].strip()
    street = nice(r.get('Address','') or '')
    addr = ', '.join(x for x in [street, city, f"{st} {r.get('ZIP','')}".strip()] if x)
    where = street or city
    a1, a2, mode, bg = PAL.get(photo, PAL['generic_shop'])
    food = ind in ('food', 'cake')
    dl = (cat if cat else label).lower()
    dl = re.sub(r'\bhvac\b', 'HVAC', dl); dl = re.sub(r'\bit\b', 'IT', dl); dl = dl.replace('texmex', 'Tex-Mex')
    if st == 'TX' and photo == 'bbq': h1 = 'Low and slow, *the Texas way.*'
    art = 'an' if dl[:1].lower() in 'aeio' or dl.startswith('HVAC') else 'a'
    lead = (f"{name} is {art} {dl} in {city}, {st}." + (f" Find it at {street}." if street else '') +
            (f" Call {phone}." if phone else ''))
    words = name.split()
    logo = [name, label] if len(name) <= 22 else [' '.join(words[:3]), ' '.join(words[3:]) or label]
    d = dict(slug=r['_slug'], name=name, short=name, ind=('food' if food else 'service'), city=city, st=st, phone=phone,
             where=where, address=addr, eyebrow=f"{city}, {st} · {label}" + (f" · {street.split(' ',1)[-1][:28]}" if street else ''),
             h1=h1, lead=lead, badges=[label, f"{city}, {st}", ("Call " + phone) if phone else "Locally owned"],
             svc_title=('On the menu.' if food else 'What we do.'),
             svc_text=('Favorites and prices would be added with the owner.' if food else 'Typical services. The owner would confirm the list and pricing.'),
             about_title=f"Local to {city}",
             about=[f"{name} is {art} {dl} serving {city}, {st} and nearby.",
                    (f"You’ll find it at {addr}." if street else f"It serves customers across {city}."),
                    "This preview puts services, hours, directions and a contact form in one place, so customers who search for you find you."],
             contact_title='Get in touch.', contact_text=f"Call, message or send a request below. {name} gets back to you.",
             form_hint='What you need and the best way to reach you', submit='Send My Request',
             viewed='Nov 24, 2026', sources=[f"Business name, category, address and phone: public business listing (Overture Maps), {r.get('Source Record','')}",
                    f"Website check {r.get('Website Check Date','')}: {r.get('Website Signal','')}"],
             brand=dict(a1=a1, a2=a2, mode=mode, bg=bg), font=FONT.get(ind, 'oswald' if photo in ('autobody','autorepair2','tires','towing','tint','detailing','roofing','fence','gym','martial','electric','handyman','carpenter','tree') else 'playfair'),
             logo=logo, photo=photo, cta2=('See the Menu' if food else 'See Services'), hours='')
    d['menu' if food else 'services'] = svc
    return d

if __name__ == '__main__':
    ghp = sys.argv[1]; rows = json.load(open(sys.argv[2])); outj = sys.argv[3]
    existing = set(os.listdir(ghp)); used = set(); out = []
    for r in rows:
        s = f"{slug(r['Business'])}-{slug(r['City'])}"
        if s in existing or s in used: s = f"{s}-{r['State'].lower()}"
        n = 2
        while s in existing or s in used: s = f"{s}-{n}"; n += 1
        used.add(s); r['_slug'] = s
        d = make(r); build(d, ghp); r['_photo'] = d['photo']; r['_name'] = d['name']; r['_label'] = d['eyebrow']
        out.append(r)
    json.dump(out, open(outj, 'w'))
    print(len(out))
