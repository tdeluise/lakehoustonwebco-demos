const {chromium}=require('playwright');const fs=require('fs');
const [BASE,OUT,JOBS]=process.argv.slice(2);
const esc=s=>String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
(async()=>{const b=await chromium.launch();
const desk=await b.newPage({viewport:{width:1280,height:800}});
const mob=await (await b.newContext({viewport:{width:390,height:780},deviceScaleFactor:2,isMobile:true,hasTouch:true})).newPage();
const comp=await b.newPage({viewport:{width:1200,height:675},deviceScaleFactor:1});
for(const j of JSON.parse(fs.readFileSync(JOBS,'utf8'))){try{
 const u=`${BASE}/${j.slug}/`;
 await desk.goto(u,{waitUntil:'load',timeout:30000});await desk.addStyleTag({content:'.bgimg{animation:none!important}'});await desk.waitForTimeout(700);
 const D=(await desk.screenshot({type:'jpeg',quality:90})).toString('base64');
 await mob.goto(u,{waitUntil:'load',timeout:30000});await mob.addStyleTag({content:'.bgimg{animation:none!important}'});await mob.waitForTimeout(700);
 const M=(await mob.screenshot({type:'jpeg',quality:90})).toString('base64');
 const a1=await desk.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--a1').trim());
 const r=j.rating?`<div class="rt"><span class="s">★</span><b>${esc(j.rating[0])}</b> from ${esc(j.rating[1])} ${esc(j.rating[2]||'Google')} reviews</div><div class="rt2">— great reputation, nowhere to send them</div>`:'';
 const body={'No website':`People searching for ${esc(j.name)} find a map pin — and nowhere to learn more or get in touch.`,'Only a social page':`Customers land on a social feed, not a page with services, hours and a call button.`,'Only a booking page':`A booking widget, but no page that shows the work, the story and how to reach you.`,'Only an ordering page':`An ordering link, but no page of its own in Google results.`}[j.head];
 await comp.setContent(`<!doctype html><html><head><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>
 *{box-sizing:border-box}body{margin:0;width:1200px;height:675px;font-family:Inter,Arial,sans-serif;display:flex;background:#f4f2ee;color:#17140f;overflow:hidden}
 .l{width:400px;background:#fff;padding:44px 40px;display:flex;flex-direction:column;border-right:1px solid #e6e2db}
 .k{font-size:13px;font-weight:700;letter-spacing:.16em;color:#8a847a}.n{font-size:31px;font-weight:800;margin:14px 0 6px;line-height:1.12}.c{color:#6d675e;font-size:16px}
 .box{margin-top:26px;border:2px dashed #d9d4cb;border-radius:18px;padding:24px;background:repeating-linear-gradient(135deg,#faf9f6 0 14px,#f3f1ec 14px 28px)}
 .box h3{margin:0 0 10px;font-size:25px}.box p{margin:0;font-size:16px;line-height:1.5;color:#4e483f}
 .rt{margin-top:24px;font-size:16px;color:#3c372f}.rt b{font-size:17px}.s{color:#f5a623;margin-right:6px}.rt2{color:#8a847a;font-size:15px;margin-top:6px}
 .f{margin-top:auto;font-size:13px;color:#6d675e}.f b{color:#17140f}
 .r{flex:1;position:relative;padding:44px 0 0 64px}.r .k{color:${a1}}.r h2{font-size:30px;margin:12px 0 22px;font-weight:800}
 .br{width:640px;border-radius:12px;overflow:hidden;box-shadow:0 30px 60px -20px rgba(0,0,0,.35);background:#fff;border:1px solid #ddd}
 .bar{height:30px;background:#efedea;display:flex;align-items:center;gap:6px;padding:0 12px}.bar i{width:10px;height:10px;border-radius:50%;background:#cfcac2}.bar span{margin-left:12px;background:#fff;border-radius:6px;font-size:11.5px;padding:3px 10px;color:#555;flex:1}
 .br img{width:100%;display:block}.ph{position:absolute;right:28px;bottom:-40px;width:188px;border:7px solid #111;border-radius:28px;overflow:hidden;box-shadow:0 24px 50px rgba(0,0,0,.4);background:#111}.ph img{width:100%;display:block}
 .arr{position:absolute;left:374px;top:310px;width:52px;height:52px;border-radius:50%;background:${a1};color:#fff;display:grid;place-items:center;font-size:24px;z-index:3;box-shadow:0 8px 20px rgba(0,0,0,.2)}
 </style></head><body><div class="l"><div class="k">TODAY</div><div class="n">${esc(j.name)}</div><div class="c">${esc(j.cat)} · ${esc(j.city)}, TX</div>
 <div class="box"><h3>${esc(j.head)}</h3><p>${body}</p></div>${r}<div class="f">Free website concept by &nbsp;<b>Lake Houston Web Co.</b></div></div>
 <div class="arr">→</div><div class="r"><div class="k" style="letter-spacing:.16em;font-weight:700;font-size:13px">WITH A NEW WEBSITE</div><h2>Ready for customers on every screen.</h2>
 <div class="br"><div class="bar"><i></i><i></i><i></i><span>lakehoustonwebco.com/${esc(j.slug)}/</span></div><img src="data:image/jpeg;base64,${D}"></div>
 <div class="ph"><img src="data:image/jpeg;base64,${M}"></div></div></body></html>`,{waitUntil:'networkidle'});
 await comp.screenshot({path:`${OUT}/${j.slug}.jpg`,type:'jpeg',quality:86});console.log('ok',j.slug);
}catch(e){console.log('ERR',j.slug,String(e).slice(0,150))}}
await b.close()})();
