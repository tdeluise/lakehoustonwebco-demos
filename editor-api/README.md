# Owner phone editor

Customers change their own website from their phone: a "Closed today" announcement,
hours, specials, menu, photos, phone number, tagline and About text. English and Spanish.

```
Owner's phone ──► editor/ (GitHub Pages)  ──►  editor-api/worker.js (Cloudflare, free)
                                                   │ checks the owner's private key
                                                   │ validates the change
                                                   ▼
                                     commits _tools/sites/<slug>.json (and photos)
                                                   ▼
                    .github/workflows/build-sites.yml rebuilds <slug>/index.html
                                                   ▼
                                  GitHub Pages publishes it (about 1–2 minutes)
```

What an owner **can** change: announcement, hours, specials, menu, photos, phone, tagline, About.
What they **can't**: name, address, theme, reviews, sources, anything else. Those still go through you.

## One-time setup (about 15 minutes, on a computer)

1. **Merge this branch into `main`** and push.

2. **Make a GitHub token** the editor uses to save changes:
   github.com → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token.
   - Repository access: **Only select repositories** → `lakehoustonwebco-demos`
   - Repository permissions: **Contents → Read and write** (nothing else)
   - Expiration: 1 year. Put a reminder on your calendar to renew it.
   Copy the token. You paste it once in step 3; don't save it anywhere else.

3. **Put the editor API on Cloudflare** (free account at dash.cloudflare.com):
   ```bash
   cd editor-api
   npx wrangler login
   npx wrangler secret put GITHUB_TOKEN     # paste the token from step 2
   npx wrangler deploy
   ```
   `deploy` prints a URL like `https://lhwc-site-editor.<your-name>.workers.dev`.

4. **Point the editor at it**: paste that URL into `editor/config.js` (`window.EDITOR_API`), commit, push.

5. **Check the rebuild Action can push**: repo → Settings → Actions → General → Workflow permissions →
   **Read and write permissions** → Save.

## For each paying customer

1. Their site must be built from a data file: `_tools/sites/<slug>.json`.
   The 7 Bryan sites already are. The older hand-made demos need converting first.
2. Make their private link:
   ```bash
   python3 _tools/new_edit_link.py <slug> "Maria (owner)"
   git add _tools/edit_keys.json && git commit -m "Edit link for <slug>" && git push
   ```
   It prints the link **once**. Text it to the owner. Tapping it opens their editor. Tell them to
   "Add to Home Screen" (the editor shows them how).
3. Lost phone, or an employee left? `python3 _tools/new_edit_link.py --revoke <slug>`, push, and make a new link.
   `--list` shows who has links.

`_tools/edit_keys.json` only stores a fingerprint (SHA-256) of each key, so it's safe in this public repo.

When a site moves to the owner's own domain, add `"domain": "theirbusiness.com"` to its JSON so the editor's
"View my website" button goes there.

## Testing locally

```bash
node --test editor-api/worker.test.mjs            # API rules and validation
node editor-api/dev-server.mjs /path/to/a/copy 8787
```
The dev server runs the real Worker code, but saves to the folder instead of GitHub and rebuilds right away.
Open `http://localhost:8787/lakehoustonwebco-demos/editor/#k=<key>` with a key made by `new_edit_link.py`
in that copy. Use a **copy** of the repo, because test edits change the files.

## Costs

Cloudflare Workers free plan: 100,000 requests a day. GitHub Pages and Actions: free for a public repo.
A small business making a few edits a week costs nothing.
