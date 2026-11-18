// Local test server: the real Worker code, with GitHub swapped for a folder on disk.
//
//   node editor-api/dev-server.mjs [repo-folder] [port]
//
// Serves the sites at http://localhost:8787/lakehoustonwebco-demos/ (like GitHub Pages),
// the editor at /lakehoustonwebco-demos/editor/, and the API at /api/*.
// After each saved edit it runs the generator for that site, the way the GitHub Action does.
// Point it at a COPY of the repo if you don't want test edits in your working tree.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import worker from "./worker.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(process.argv[2] || path.join(here, ".."));
const port = Number(process.argv[3] || 8787);
const PREFIX = "/lakehoustonwebco-demos/";

const sha = (buf) => crypto.createHash("sha1").update(buf).digest("hex");
const store = {
  async get(p) {
    const f = path.join(root, p);
    if (!fs.existsSync(f)) return null;
    const buf = fs.readFileSync(f);
    return { text: buf.toString("utf8"), sha: sha(buf) };
  },
  async put(p, b64, expectedSha, message) {
    const f = path.join(root, p);
    if (expectedSha && fs.existsSync(f) && sha(fs.readFileSync(f)) !== expectedSha) {
      const e = new Error("conflict");
      e.status = 409;
      throw e;
    }
    const buf = Buffer.from(b64, "base64");
    fs.mkdirSync(path.dirname(f), { recursive: true });
    fs.writeFileSync(f, buf);
    console.log(`[commit] ${message}`);
    const m = p.match(/^_tools\/sites\/([a-z0-9-]+)\.json$/);
    if (m) {
      execFileSync("python3", [path.join(root, "_tools/build_demos.py"), root, m[1]], { stdio: "inherit" });
    }
    return sha(buf);
  },
};

const env = {
  __store: store,
  ALLOWED_ORIGINS: `http://localhost:${port},http://127.0.0.1:${port}`,
  SITE_BASE: `http://localhost:${port}${PREFIX}`,
};

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".webmanifest": "application/manifest+json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".txt": "text/plain" };

http
  .createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);
    if (url.pathname.startsWith("/api/")) {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      const body = chunks.length ? Buffer.concat(chunks) : undefined;
      const r = await worker.fetch(new Request(url, { method: req.method, headers: req.headers, body: ["GET", "HEAD", "OPTIONS"].includes(req.method) ? undefined : body }), env);
      res.writeHead(r.status, Object.fromEntries(r.headers));
      res.end(Buffer.from(await r.arrayBuffer()));
      return;
    }
    if (!url.pathname.startsWith(PREFIX)) {
      res.writeHead(302, { location: PREFIX });
      return res.end();
    }
    let f = path.join(root, decodeURIComponent(url.pathname.slice(PREFIX.length)));
    if (!f.startsWith(root)) return res.writeHead(403).end();
    if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, "index.html");
    if (!fs.existsSync(f)) return res.writeHead(404).end("not found");
    res.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream", "cache-control": "no-store" });
    fs.createReadStream(f).pipe(res);
  })
  .listen(port, () => console.log(`Editor dev server: http://localhost:${port}${PREFIX}editor/  (repo: ${root})`));
