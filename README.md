# Lake Houston Web Co — demo previews

One folder per business: `/<slug>/index.html`. Served by GitHub Pages at
`https://tdeluise.github.io/lakehoustonwebco-demos/<slug>/`.

Every demo keeps `<meta name="robots" content="noindex">` and the footer
"Demo site prepared by Lake Houston Web Co". Remove both only when a client
pays and the site moves to their own domain. Photo credits and fact notes live
in each folder's `SOURCES.txt`.

## Data-driven sites and the owner editor

Sites built by `_tools/build_demos.py` come from one file each: `_tools/sites/<slug>.json`.
Rebuild with `python3 _tools/build_demos.py . [slug ...]` (a GitHub Action also does this on push).

Paying customers can edit their own site from their phone (hours, announcements, specials, menu,
photos, phone, tagline, About) at `/editor/`. Setup and per-customer steps: `editor-api/README.md`.
