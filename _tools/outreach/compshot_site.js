// usage: node compshot_site.js <gh-pages checkout> <out dir> <jobs.json>
// jobs.json: [{"slug": "...", "site": "https://their-current-site.com", "issues": ["Not secure", ...]}]
// For businesses that already have a weak website. Builds the same
// "What you have now vs. The demo I made you" image as compshot.js, but the left
// side is a real phone screenshot of their current site with the problems labeled.
// No customer data lives in this file; pass it in via jobs.json (keep that out of the repo).
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path');
const [GHP, OUT, JOBS] = process.argv.slice(2);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
(async () => {
  const b = await chromium.launch();
  const mob = {viewport: {width: 390, height: 760}, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'};
  const ctx = await b.newContext(mob);
  const cur = await ctx.newPage(), ph = await ctx.newPage();
  const comp = await b.newPage({viewport: {width: 1000, height: 600}});
  for (const j of JSON.parse(fs.readFileSync(JOBS, 'utf8'))) {
    try {
      await cur.goto(j.site, {waitUntil: 'load', timeout: 25000});
      await cur.waitForTimeout(2500);
      for (let k = 0; k < 4; k++) {
        const t = (await cur.evaluate(() => document.body ? document.body.innerText.slice(0, 400) : '')).toLowerCase();
        if (!/(please wait|verif|checking your browser|just a moment|captcha|access denied)/.test(t)) break;
        if (k === 3) throw new Error('blocked by a bot check, screenshot their site by hand');
        await cur.waitForTimeout(4000);
      }
      const now = (await cur.screenshot({type: 'png'})).toString('base64');
      const url = 'file://' + path.resolve(GHP) + '/' + j.slug + '/index.html';
      await ph.goto(url, {waitUntil: 'load', timeout: 20000});
      await ph.addStyleTag({content: '.reveal{opacity:1!important;transform:none!important;transition:none!important}.callbar{display:none!important}'});
      await ph.waitForTimeout(400);
      const demo = (await ph.screenshot({type: 'png'})).toString('base64');
      const accent = await ph.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--a1').trim() || '#1d6b74');
      const host = new URL(j.site).host.replace(/^www\./, '');
      const chips = (j.issues || []).slice(0, 3).map(i => `<div class="chip">&#x2715; ${esc(i)}</div>`).join('');
      await comp.setContent(`<!doctype html><html><head><style>
  *{box-sizing:border-box}body{margin:0;width:1000px;background:#f3f5f4;font:16px/1.3 Arial,Helvetica,sans-serif;color:#13262a}
  .wrap{display:flex;gap:28px;padding:30px 34px 34px;align-items:stretch}
  .col{flex:1;display:flex;flex-direction:column;align-items:center}
  .lab{font-weight:800;font-size:15px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 14px;padding:7px 14px;border-radius:999px}
  .l .lab{background:#e3e7e6;color:#4a5b5e}.r .lab{background:${accent};color:#fff}
  .phone{width:270px;border:9px solid #13262a;border-radius:32px;overflow:hidden;background:#fff;box-shadow:0 14px 34px rgba(0,0,0,.22)}
  .phone img{width:100%;display:block}
  .bar{background:#eceff1;color:#5b6b70;font-size:11px;padding:5px 10px;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .l .phone{filter:saturate(.85)}
  .chips{margin-top:14px;display:flex;flex-direction:column;gap:6px;align-items:center}
  .chip{background:#fde8e8;color:#9b1c1c;font-size:13px;font-weight:700;padding:5px 12px;border-radius:999px}
  .vs{align-self:center;font-weight:900;font-size:22px;color:#8a9a9c}
  </style></head><body><div class="wrap">
  <div class="col l"><div class="lab">What you have now</div><div class="phone"><div class="bar">${esc(host)}</div><img src="data:image/png;base64,${now}"></div><div class="chips">${chips}</div></div>
  <div class="vs">vs</div>
  <div class="col r"><div class="lab">The demo I made you</div><div class="phone"><div class="bar">lakehoustonwebco.com/${esc(j.slug)}</div><img src="data:image/png;base64,${demo}"></div></div>
  </div></body></html>`);
      await comp.waitForTimeout(150);
      const h = await comp.evaluate(() => document.body.scrollHeight);
      await comp.setViewportSize({width: 1000, height: h});
      await comp.screenshot({path: `${OUT}/${j.slug}.jpg`, type: 'jpeg', quality: 82, fullPage: true});
      console.log('ok', j.slug);
    } catch (e) { console.log('ERR', j.slug, String(e).slice(0, 120)); }
  }
  await b.close();
})();
