// Lake Houston Web Co — site editor API (Cloudflare Worker, no dependencies).
//
// The owner's phone app (editor/) calls this with their private edit key.
// The Worker checks the key, validates the change, and commits it to GitHub:
//   _tools/sites/<slug>.json     owner-editable business data
//   <slug>/assets/owner-*.jpg    photos the owner uploads
// A GitHub Action (.github/workflows/build-sites.yml) then rebuilds <slug>/index.html.
//
// Edit keys are never stored. _tools/edit_keys.json (public, in the repo) maps the
// SHA-256 of each key to a slug. Make one with: python3 _tools/new_edit_link.py <slug>
//
// Environment (wrangler.toml / dashboard):
//   GITHUB_TOKEN    secret: fine-grained token, Contents read/write on this one repo
//   GITHUB_REPO     "tdeluise/lakehoustonwebco-demos"
//   GITHUB_BRANCH   "main"
//   ALLOWED_ORIGINS comma-separated origins allowed to call the API
//   SITE_BASE       public URL that the sites are served under, ending in "/"

const KEYS_PATH = "_tools/edit_keys.json";
const sitePath = (slug) => `_tools/sites/${slug}.json`;
const MAX_PHOTO_BYTES = 3 * 1024 * 1024;
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request, env);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    try {
      const res = await route(request, env);
      for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
      return res;
    } catch (err) {
      const status = err.status || 500;
      if (status === 500) console.error(err && err.stack ? err.stack : err);
      return json({ error: status === 500 ? "Something went wrong. Try again in a minute." : err.message }, status, cors);
    }
  },
};

async function route(request, env) {
  const url = new URL(request.url);
  const store = env.__store || githubStore(env);
  if (url.pathname === "/" || url.pathname === "/api/health") return json({ ok: true });

  const slug = await authenticate(request, store);

  if (url.pathname === "/api/site" && request.method === "GET") {
    const file = await store.get(sitePath(slug));
    if (!file) throw httpError(404, "This site has no editable data yet. Contact Lake Houston Web Co.");
    const data = JSON.parse(file.text);
    return json(view(slug, data, file.sha, env));
  }

  if (url.pathname === "/api/site" && request.method === "PUT") {
    const body = await readJson(request, 200_000);
    const file = await store.get(sitePath(slug));
    if (!file) throw httpError(404, "This site has no editable data yet.");
    if (body.version && body.version !== file.sha) {
      throw httpError(409, "Your site was changed somewhere else. Reload to see the latest, then make your change again.");
    }
    const data = JSON.parse(file.text);
    const changed = applyEdits(data, body.fields || {});
    if (!changed.length) return json(view(slug, data, file.sha, env));
    const text = JSON.stringify(data, null, 2) + "\n";
    const sha = await store.put(sitePath(slug), utf8ToBase64(text), file.sha, `Owner edit (${slug}): ${changed.join(", ")}`);
    return json({ ...view(slug, data, sha, env), changed });
  }

  if (url.pathname === "/api/photo" && request.method === "POST") {
    const len = Number(request.headers.get("content-length") || 0);
    if (len > MAX_PHOTO_BYTES) throw httpError(413, "That photo is too large.");
    const bytes = new Uint8Array(await request.arrayBuffer());
    if (bytes.length > MAX_PHOTO_BYTES) throw httpError(413, "That photo is too large.");
    const ext = imageType(bytes);
    if (!ext) throw httpError(415, "Please choose a JPG, PNG or WebP photo.");
    const name = `owner-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}-${randomHex(4)}.${ext}`;
    await store.put(`${slug}/assets/${name}`, bytesToBase64(bytes), null, `Owner photo (${slug}): ${name}`);
    return json({ src: `assets/${name}` });
  }

  throw httpError(404, "Not found");
}

// ---------- auth ----------

let keysCache = { at: 0, map: null };

async function authenticate(request, store) {
  const h = request.headers.get("authorization") || "";
  const key = h.startsWith("Bearer ") ? h.slice(7).trim() : "";
  if (!/^[A-Za-z0-9_-]{20,100}$/.test(key)) throw httpError(401, "This edit link isn't valid. Ask Lake Houston Web Co for a new one.");
  if (!keysCache.map || Date.now() - keysCache.at > 60_000) {
    const file = await store.get(KEYS_PATH);
    keysCache = { at: Date.now(), map: file ? JSON.parse(file.text) : {} };
  }
  const entry = keysCache.map[await sha256Hex(key)];
  const slug = entry && (typeof entry === "string" ? entry : entry.slug);
  if (!slug || !/^[a-z0-9-]+$/.test(slug)) throw httpError(401, "This edit link isn't valid or was turned off. Ask Lake Houston Web Co for a new one.");
  return slug;
}

export function _resetKeyCache() {
  keysCache = { at: 0, map: null };
}

// ---------- what the editor sees / may change ----------

function view(slug, d, sha, env) {
  const base = (env.SITE_BASE || "").replace(/\/?$/, "/");
  return {
    slug,
    name: d.name,
    live_url: d.domain ? `https://${d.domain}/` : `${base}${slug}/`,
    version: sha,
    has_locations: Array.isArray(d.locations) && d.locations.length > 0,
    fields: {
      notice: d.notice || null,
      specials: d.specials || [],
      photos: d.photos || [],
      items: d.items || [],
      items_title: d.items_title || "Menu",
      phone: d.phone || "",
      address: d.address || "",
      hours: d.hours || null,
      hours_note: d.hours_note || "",
      locations: (d.locations || []).map((L) => ({ label: L.label || "", address: L.address || "", phone: L.phone || "", hours: L.hours || null, hours_note: L.hours_note || "" })),
      tagline: d.tagline || "",
      about: d.about || [],
    },
  };
}

// Validates every field the owner sent and writes it into the site data.
// Returns the list of field names that actually changed.
export function applyEdits(d, f) {
  const changed = [];
  const set = (key, value) => {
    const empty = value === null || value === "" || (Array.isArray(value) && value.length === 0);
    if (JSON.stringify(d[key] ?? null) === JSON.stringify(empty ? null : value)) return;
    if (empty) delete d[key];
    else d[key] = value;
    changed.push(key);
  };

  if ("notice" in f) {
    const n = f.notice;
    if (!n || !String(n.text || "").trim()) set("notice", null);
    else {
      const until = str(n.until, 10, "End date");
      if (until && !/^\d{4}-\d{2}-\d{2}$/.test(until)) throw httpError(400, "End date must look like 2026-11-20.");
      set("notice", until ? { text: str(n.text, 200, "Announcement"), until } : { text: str(n.text, 200, "Announcement") });
    }
  }
  if ("specials" in f) {
    set("specials", list(f.specials, 12, "specials").map((x) => clean({
      title: str(x.title, 60, "Special name"), text: str(x.text, 240, "Special details"), price: str(x.price, 20, "Price"),
    })).filter((x) => x.title));
  }
  if ("photos" in f) {
    set("photos", list(f.photos, 24, "photos").map((x) => {
      const src = String(x.src || "");
      if (!/^assets\/[A-Za-z0-9._-]+\.(jpe?g|png|webp)$/.test(src)) throw httpError(400, "One of the photos isn't valid.");
      return { src, alt: str(x.alt, 120, "Photo description") };
    }));
  }
  if ("items" in f) {
    set("items", list(f.items, 12, "menu sections").map((g) => clean({
      title: str(g.title, 60, "Section name"),
      list: list(g.list, 60, "menu items").map((i) => str(i, 140, "Menu item")).filter(Boolean),
    })).filter((g) => g.list && g.list.length));
  }
  if ("items_title" in f) {
    const t = str(f.items_title, 30, "Menu heading");
    if ((d.items_title || "Menu") !== (t || "Menu")) set("items_title", t && t !== "Menu" ? t : null);
  }
  if ("phone" in f) set("phone", phone(f.phone));
  if ("tagline" in f) {
    const t = str(f.tagline, 160, "Tagline");
    if (!t) throw httpError(400, "The tagline can't be empty.");
    set("tagline", t);
  }
  if ("about" in f) set("about", list(f.about, 8, "paragraphs").map((p) => str(p, 900, "About")).filter(Boolean));
  if ("hours" in f) {
    if (Array.isArray(d.locations) && d.locations.length) throw httpError(400, "Edit hours under each location.");
    if (f.hours) set("hours", hours(f.hours)); // null = keep what's there (e.g. a written hours note)
  }
  if ("locations" in f) {
    const locs = list(f.locations, 10, "locations");
    if (!Array.isArray(d.locations) || locs.length !== d.locations.length) throw httpError(400, "Locations can't be added or removed here. Contact Lake Houston Web Co.");
    const next = d.locations.map((L, i) => clean({ ...L, phone: phone(locs[i].phone), hours: locs[i].hours ? hours(locs[i].hours) : undefined }));
    if (JSON.stringify(next) !== JSON.stringify(d.locations)) {
      d.locations = next;
      changed.push("locations");
    }
  }
  // "Hours as listed on Google…" stops being true once the owner sets their own hours.
  if ((changed.includes("hours") || changed.includes("locations")) && d.hours_source) delete d.hours_source;
  return changed;
}

function hours(h) {
  if (typeof h !== "object" || Array.isArray(h)) throw httpError(400, "Hours aren't valid.");
  const out = {};
  for (const day of DAYS) out[day] = str(h[day], 40, `${day} hours`) || "Closed";
  return out;
}

function phone(p) {
  const s = str(p, 20, "Phone");
  if (s && !/^[0-9()+\-. ]{7,20}$/.test(s)) throw httpError(400, "The phone number has characters that don't belong in a phone number.");
  return s;
}

function str(v, max, label) {
  if (v === undefined || v === null) return "";
  if (typeof v !== "string" && typeof v !== "number") throw httpError(400, `${label} isn't valid.`);
  const s = String(v).replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, "").replace(/\s+/g, " ").trim();
  if (s.length > max) throw httpError(400, `${label} is too long (${max} characters max).`);
  return s;
}

function list(v, max, label) {
  if (v === undefined || v === null) return [];
  if (!Array.isArray(v)) throw httpError(400, `The ${label} list isn't valid.`);
  if (v.length > max) throw httpError(400, `Too many ${label} (${max} max).`);
  return v.map((x) => (x && typeof x === "object" ? x : typeof x === "string" ? x : {}));
}

function clean(o) {
  for (const k of Object.keys(o)) if (o[k] === "" || o[k] === undefined) delete o[k];
  return o;
}

// ---------- GitHub contents store ----------

function githubStore(env) {
  const repo = env.GITHUB_REPO;
  const branch = env.GITHUB_BRANCH || "main";
  if (!env.GITHUB_TOKEN || !repo) throw new Error("GITHUB_TOKEN and GITHUB_REPO must be set");
  const api = (path) => `https://api.github.com/repos/${repo}/contents/${path.split("/").map(encodeURIComponent).join("/")}`;
  const headers = {
    authorization: `Bearer ${env.GITHUB_TOKEN}`,
    accept: "application/vnd.github+json",
    "user-agent": "site-editor-worker",
    "x-github-api-version": "2022-11-28",
  };
  return {
    async get(path) {
      const r = await fetch(`${api(path)}?ref=${encodeURIComponent(branch)}`, { headers });
      if (r.status === 404) return null;
      if (!r.ok) throw new Error(`GitHub GET ${path}: ${r.status} ${await r.text()}`);
      const j = await r.json();
      return { text: base64ToUtf8(j.content), sha: j.sha };
    },
    async put(path, contentBase64, sha, message) {
      const body = { message, content: contentBase64, branch };
      if (sha) body.sha = sha;
      const r = await fetch(api(path), { method: "PUT", headers: { ...headers, "content-type": "application/json" }, body: JSON.stringify(body) });
      if (r.status === 409 || r.status === 422) throw httpError(409, "Your site was changed somewhere else. Reload and try again.");
      if (!r.ok) throw new Error(`GitHub PUT ${path}: ${r.status} ${await r.text()}`);
      return (await r.json()).content.sha;
    },
  };
}

// ---------- helpers ----------

function corsHeaders(request, env) {
  const origin = request.headers.get("origin") || "";
  const allowed = String(env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const h = { "access-control-allow-methods": "GET, PUT, POST, OPTIONS", "access-control-allow-headers": "authorization, content-type", "access-control-max-age": "86400", vary: "origin" };
  if (origin && allowed.includes(origin)) h["access-control-allow-origin"] = origin;
  return h;
}

function json(obj, status = 200, extra = {}) {
  return new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extra } });
}

function httpError(status, message) {
  const e = new Error(message);
  e.status = status;
  return e;
}

async function readJson(request, max) {
  const text = await request.text();
  if (text.length > max) throw httpError(413, "That change is too large.");
  try {
    return JSON.parse(text);
  } catch {
    throw httpError(400, "Bad request.");
  }
}

function imageType(b) {
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return "jpg";
  if (b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47) return "png";
  if (b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 && b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50) return "webp";
  return null;
}

async function sha256Hex(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

function randomHex(n) {
  return [...crypto.getRandomValues(new Uint8Array(n))].map((x) => x.toString(16).padStart(2, "0")).join("");
}

function bytesToBase64(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

function utf8ToBase64(s) {
  return bytesToBase64(new TextEncoder().encode(s));
}

function base64ToUtf8(b64) {
  const bin = atob(String(b64).replace(/\s/g, ""));
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}
