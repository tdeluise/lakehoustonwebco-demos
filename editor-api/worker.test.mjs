// Run: node --test editor-api/
import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import worker, { applyEdits, _resetKeyCache } from "./worker.js";

const KEY = "test-key-abcdefghijklmnopqrstuvwxyz";
const hash = (s) => crypto.createHash("sha256").update(s).digest("hex");

function memoryStore(files) {
  const commits = [];
  let n = 0;
  return {
    files,
    commits,
    async get(p) {
      return p in files ? { text: Buffer.from(files[p].b64, "base64").toString("utf8"), sha: files[p].sha } : null;
    },
    async put(p, b64, sha, message) {
      if (sha && files[p] && files[p].sha !== sha) throw Object.assign(new Error("conflict"), { status: 409 });
      files[p] = { b64, sha: `sha${++n}` };
      commits.push(message);
      return files[p].sha;
    },
  };
}

function setup(site = {}) {
  _resetKeyCache();
  const enc = (o) => Buffer.from(JSON.stringify(o)).toString("base64");
  const store = memoryStore({
    "_tools/edit_keys.json": { b64: enc({ [hash(KEY)]: { slug: "lionels" } }), sha: "k1" },
    "_tools/sites/lionels.json": {
      b64: enc({ slug: "lionels", name: "Lionel's", tagline: "Old-school cuts", phone: "", address: "1 Main St", hours: { Monday: "Closed" }, hours_source: "As listed on Google.", sources: ["x"], ...site }),
      sha: "s1",
    },
  });
  const env = { __store: store, ALLOWED_ORIGINS: "https://tdeluise.github.io", SITE_BASE: "https://tdeluise.github.io/lakehoustonwebco-demos/" };
  const call = (method, path, body, headers = {}) =>
    worker.fetch(new Request("https://api.test" + path, {
      method,
      headers: { authorization: `Bearer ${KEY}`, origin: "https://tdeluise.github.io", ...headers },
      body: body === undefined ? undefined : body instanceof Uint8Array ? body : JSON.stringify(body),
    }), env);
  const siteData = () => JSON.parse(Buffer.from(store.files["_tools/sites/lionels.json"].b64, "base64").toString("utf8"));
  return { store, call, siteData };
}

test("rejects missing, malformed and unknown keys", async () => {
  const { call } = setup();
  assert.equal((await call("GET", "/api/site", undefined, { authorization: "" })).status, 401);
  assert.equal((await call("GET", "/api/site", undefined, { authorization: "Bearer short" })).status, 401);
  assert.equal((await call("GET", "/api/site", undefined, { authorization: "Bearer " + "z".repeat(32) })).status, 401);
});

test("GET returns the editable view with CORS for the allowed origin only", async () => {
  const { call } = setup();
  const r = await call("GET", "/api/site");
  assert.equal(r.status, 200);
  assert.equal(r.headers.get("access-control-allow-origin"), "https://tdeluise.github.io");
  const j = await r.json();
  assert.equal(j.slug, "lionels");
  assert.equal(j.live_url, "https://tdeluise.github.io/lakehoustonwebco-demos/lionels/");
  assert.equal(j.fields.tagline, "Old-school cuts");
  assert.equal(j.fields.sources, undefined, "internal fields are not exposed");
  const other = await call("GET", "/api/site", undefined, { origin: "https://evil.example" });
  assert.equal(other.headers.get("access-control-allow-origin"), null);
});

test("PUT saves owner fields, keeps everything else, and commits once", async () => {
  const { call, store, siteData } = setup();
  const r = await call("PUT", "/api/site", {
    version: "s1",
    fields: {
      notice: { text: "  Closed   today  ", until: "2026-11-20" },
      specials: [{ title: "Taco Tuesday", price: "$5", text: "" }, { title: "" }],
      hours: { Monday: "9:00 AM – 5:00 PM" },
      phone: "(979) 555-0100",
      slug: "hacked", sources: [], launched: true,
    },
  });
  assert.equal(r.status, 200);
  const j = await r.json();
  assert.deepEqual(j.changed.sort(), ["hours", "notice", "phone", "specials"]);
  const d = siteData();
  assert.deepEqual(d.notice, { text: "Closed today", until: "2026-11-20" });
  assert.deepEqual(d.specials, [{ title: "Taco Tuesday", price: "$5" }]);
  assert.equal(d.hours.Monday, "9:00 AM – 5:00 PM");
  assert.equal(d.hours.Sunday, "Closed");
  assert.equal(d.slug, "lionels");
  assert.deepEqual(d.sources, ["x"]);
  assert.equal(d.launched, undefined);
  assert.equal(d.hours_source, undefined, "the 'as listed on Google' note goes once the owner sets hours");
  assert.equal(store.commits.length, 1);
  assert.match(store.commits[0], /^Owner edit \(lionels\): /);
});

test("PUT with a stale version is refused", async () => {
  const { call } = setup();
  assert.equal((await call("PUT", "/api/site", { version: "old", fields: { phone: "555-555-1234" } })).status, 409);
});

test("no-op PUT makes no commit; clearing a field removes it", async () => {
  const { call, store, siteData } = setup({ notice: { text: "Hi" } });
  let j = await (await call("PUT", "/api/site", { version: "s1", fields: { tagline: "Old-school cuts" } })).json();
  assert.deepEqual(j.changed, undefined);
  assert.equal(store.commits.length, 0);
  j = await (await call("PUT", "/api/site", { version: "s1", fields: { notice: null } })).json();
  assert.deepEqual(j.changed, ["notice"]);
  assert.equal("notice" in siteData(), false);
});

test("validation rejects bad input", () => {
  const d = () => ({ name: "x", tagline: "t", locations: [{ address: "a", hours: {} }] });
  assert.throws(() => applyEdits(d(), { photos: [{ src: "https://evil/x.jpg" }] }), /photos/);
  assert.throws(() => applyEdits(d(), { photos: [{ src: "assets/../../x.jpg" }] }), /photos/);
  assert.throws(() => applyEdits(d(), { phone: "<script>" }), /phone/);
  assert.throws(() => applyEdits(d(), { notice: { text: "x", until: "tomorrow" } }), /date/i);
  assert.throws(() => applyEdits(d(), { notice: { text: "x".repeat(201) } }), /too long/);
  assert.throws(() => applyEdits(d(), { tagline: "" }), /empty/);
  assert.throws(() => applyEdits(d(), { hours: {} }), /each location/);
  assert.throws(() => applyEdits(d(), { locations: [] }), /added or removed/);
  assert.throws(() => applyEdits(d(), { specials: new Array(13).fill({ title: "a" }) }), /Too many/);
});

test("locations: only phone and hours change", () => {
  const d = { tagline: "t", locations: [{ label: "North", address: "1 A St", phone: "", hours: null }] };
  const changed = applyEdits(d, { locations: [{ label: "HACK", address: "HACK", phone: "979-555-0101", hours: { Monday: "8:00 AM – 2:00 PM" } }] });
  assert.deepEqual(changed, ["locations"]);
  assert.equal(d.locations[0].label, "North");
  assert.equal(d.locations[0].address, "1 A St");
  assert.equal(d.locations[0].phone, "979-555-0101");
  assert.equal(d.locations[0].hours.Tuesday, "Closed");
});

test("a location with a written hours note keeps it when another location is edited", () => {
  const d = { tagline: "t", locations: [
    { label: "A", address: "1", hours_note: "Open daily from 9 AM" },
    { label: "B", address: "2", hours: { Monday: "9:00 AM – 5:00 PM" } },
  ] };
  applyEdits(d, { locations: [{ phone: "", hours: null }, { phone: "", hours: { Sunday: "Closed" } }] });
  assert.equal(d.locations[0].hours, undefined);
  assert.equal(d.locations[0].hours_note, "Open daily from 9 AM");
  assert.equal(d.locations[1].hours.Monday, "Closed");
});

test("top-level hours: null leaves them alone", () => {
  const d = { tagline: "t", hours_note: "By appointment" };
  assert.deepEqual(applyEdits(d, { hours: null }), []);
  assert.equal(d.hours_note, "By appointment");
});

test("photo upload accepts real images only and stores under the owner's folder", async () => {
  const { call, store } = setup();
  const jpeg = new Uint8Array([0xff, 0xd8, 0xff, 0xe0, 1, 2, 3, 4]);
  const r = await call("POST", "/api/photo", jpeg, { "content-type": "image/jpeg" });
  assert.equal(r.status, 200);
  const { src } = await r.json();
  assert.match(src, /^assets\/owner-\d{8}-[0-9a-f]{8}\.jpg$/);
  assert.ok(`lionels/${src}` in store.files);
  const html = new TextEncoder().encode("<html><script>");
  assert.equal((await call("POST", "/api/photo", html, { "content-type": "image/jpeg" })).status, 415);
});

test("OPTIONS preflight", async () => {
  const { call } = setup();
  const r = await call("OPTIONS", "/api/site");
  assert.equal(r.status, 204);
  assert.match(r.headers.get("access-control-allow-headers"), /authorization/);
});
