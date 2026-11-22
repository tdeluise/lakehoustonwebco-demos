// usage: node compshot.js <gh-pages checkout> <out dir> slug [slug...]  -> <out dir>/<slug>.jpg
// Builds the 'What you have now vs. The demo I made you' image used in outreach emails.
// Left: the demo's .ol-today card (what we found online). Right: phone screenshot of the demo.
const {chromium}=require('playwright');
const [GHP, SP] = [process.argv[2], process.argv[3]];
(async()=>{
 const b=await chromium.launch();
 const ph=await b.newPage({viewport:{width:390,height:760},deviceScaleFactor:2});
 const wd=await b.newPage({viewport:{width:1000,height:900},deviceScaleFactor:2});
 const comp=await b.newPage({viewport:{width:1000,height:600},deviceScaleFactor:1});
 for(const slug of process.argv.slice(4)){
  try{
   const url='file://'+require('path').resolve(GHP)+'/'+slug+'/index.html';
   await ph.goto(url,{waitUntil:'load',timeout:20000}); await ph.addStyleTag({content:'.reveal{opacity:1!important;transform:none!important;transition:none!important}.callbar{display:none!important}'}); await ph.waitForTimeout(400);
   const demo=(await ph.screenshot({type:'png'})).toString('base64');
   await wd.goto(url,{waitUntil:'load',timeout:20000}); await wd.waitForTimeout(300);
   await wd.addStyleTag({content:'.ol-grid,.vs-grid{align-items:start}.reveal{opacity:1!important;transform:none!important;transition:none!important}'});
   const card=(await wd.$('.vs-card.today'))||(await wd.$('.ol-today'));
   const today=(await card.screenshot({type:'png'})).toString('base64');
   const accent=await wd.evaluate(()=>(document.querySelector('.ol')?getComputedStyle(document.querySelector('.ol')).getPropertyValue('--ol-accent'):getComputedStyle(document.documentElement).getPropertyValue('--a1')).trim()||'#1d6b74');
   await comp.setContent(`<!doctype html><html><head><style>
   *{box-sizing:border-box}body{margin:0;width:1000px;background:#f3f5f4;font:16px/1.3 Arial,Helvetica,sans-serif;color:#13262a}
   .wrap{display:flex;gap:28px;padding:30px 34px 34px;align-items:stretch}
   .col{flex:1;display:flex;flex-direction:column;align-items:center}
   .lab{font-weight:800;font-size:15px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 14px;padding:7px 14px;border-radius:999px}
   .l .lab{background:#e3e7e6;color:#4a5b5e}.r .lab{background:${accent};color:#fff}
   .box{flex:1;display:flex;align-items:center;justify-content:center;width:100%}
   .card{width:100%;max-width:440px;background:#fff;border-radius:16px;padding:6px;box-shadow:0 6px 20px rgba(0,0,0,.08)}
   .card img{width:100%;display:block;border-radius:12px}
   .phone{width:270px;border:9px solid #13262a;border-radius:32px;overflow:hidden;background:#fff;box-shadow:0 14px 34px rgba(0,0,0,.22)}
   .phone img{width:100%;display:block}
   .vs{align-self:center;font-weight:900;font-size:22px;color:#8a9a9c}
   </style></head><body><div class="wrap">
   <div class="col l"><div class="lab">What you have now</div><div class="box"><div class="card"><img src="data:image/png;base64,${today}"></div></div></div>
   <div class="vs">vs</div>
   <div class="col r"><div class="lab">The demo I made you</div><div class="box"><div class="phone"><img src="data:image/png;base64,${demo}"></div></div></div>
   </div></body></html>`);
   await comp.waitForTimeout(150);
   const h=await comp.evaluate(()=>document.body.scrollHeight);
   await comp.screenshot({path:`${SP}/${slug}.jpg`,type:'jpeg',quality:82,clip:{x:0,y:0,width:1000,height:h}});
   console.log('ok',slug);
  }catch(e){console.log('ERR',slug,String(e).slice(0,120));}
 }
 await b.close();
})();
