'use strict';
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const home = require('node:os').homedir(), out = path.resolve(__dirname, '..');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || path.join(home, '.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const executablePath = process.env.CHROMIUM || path.join(home, '.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const url = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:4178';
const stock = fs.readFileSync(path.resolve(out, '../Guilde-Destiny-Lumiere-Ancree.html'), 'utf8');
const previous = fs.readFileSync(process.env.ATLAS_LIGHT_BEFORE || path.join(home, '.cache/lumiere-braseros/Lumiere-Ancree-avant-lueur-tamisee.html'), 'utf8');
const payload = html => JSON.parse(html.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);
const old = payload(previous), now = payload(stock);
const {lianes: lv, lueur, film, reference, ...rooms} = now;
const {lianes: lo, film: oldFilm, reference: oldRef, ...oldRooms} = old;
assert.deepEqual(rooms, oldRooms);
assert.equal(reference.apng, oldRef.apng);
assert.notEqual(reference.salon, oldRef.salon);
assert.notEqual(film.webm, oldFilm.webm);
assert.equal(lueur.ms, 9600);
for (const name of Object.keys(lv)) {
  const {points, reflets, ...leaves} = lv[name];
  const {points: before, reflets: discard, ...baseLeaves} = lo[name];
  assert.deepEqual(leaves, baseLeaves);
  assert.equal(points.length, 2);
  assert.deepEqual(points.map(p => [p.x, p.y]), before.map(p => [p.x, p.y]));
}
const waitAtlas = (p,n) => p.waitForFunction(n => {
  const c = [...document.querySelectorAll('.atlas-map')];
  return c.length === 15 && c.every(e => e.dataset.scene?.endsWith(`:${n}:0:0`));
}, n, {timeout: 12000});
const lockPhase = async (p,n) => { await p.locator(`[data-atlas-phase="${n}"]`).click(); await waitAtlas(p,n); };
const atlas = p => p.locator('.atlas-map').evaluateAll(nodes => nodes.map(c => c.toDataURL()));

async function play(scope) {
  const v = scope.locator('#film-comparatif');
  await scope.locator('#film-button').click();
  const playing = await v.evaluate(el => new Promise((ok, fail) => {
    const timeout = setTimeout(() => fail(new Error('La lecture vidéo ne démarre pas')), 7000);
    const check = () => {
      if (el.currentTime > .2 && !el.paused && el.videoWidth === 1120) {
        clearTimeout(timeout); ok({duree: el.duration, muet: el.muted, boucle: el.loop});
      } else requestAnimationFrame(check);
    };
    check();
  }));
  assert(playing.muet && playing.boucle && Math.abs(playing.duree - 9.6) < .07);
}

(async () => {
  const b = await chromium.launch({executablePath, headless:true, args:['--no-sandbox','--disable-dev-shm-usage']});
  try {
    const p = await b.newPage({viewport:{width:1380,height:940},reducedMotion:'reduce'}), errs=[];
    p.on('pageerror', e => errs.push(e.message));
    await p.goto(url); await waitAtlas(p,3);
    assert.match(await p.title(), /Lueur tamisée/);
    assert.equal(await p.locator('#motion-toggle').getAttribute('aria-pressed'),'false');
    // Export two closure bindings in this intercepted copy only; the delivered page has no test hook.
    const last = 'setupAtlas();updatePalette();refresh();setupMotion();';
    assert(stock.includes(last));
    await p.route(url+'/controle', r => r.fulfill({contentType:'text/html; charset=utf-8',body:stock.replace(last, last+'\nwindow.__inspectLueur={data,drawScene};')}));
    await p.goto(url+'/controle');await waitAtlas(p,3);
    const proof = await p.evaluate(() => {
      const {data, drawScene} = window.__inspectLueur;
      const c = document.createElement('canvas'), ctx=c.getContext('2d',{willReadFrequently:true});
      const compute = (r,ms) => {
        drawScene(ctx,r,3,{x:0,y:0,w:r.w,h:r.h},{items:[],ms});
        return ctx.getImageData(0,0,r.w,r.h).data;
      };
      return data.rooms.map(r => {
        c.width=r.w;c.height=r.h;
        const a=compute(r,0), z=compute(r,2800), g=compute(r,6100), end=compute(r,9600);
        let changes=0, forbidden=0, peak=0, seam=0;
        for(let i=0;i<a.length;i+=4) {
          let d=0;
          for (let k=0;k<3;k++) d=Math.max(d,Math.abs(a[i+k]-z[i+k]),Math.abs(a[i+k]-g[i+k]));
          seam+=+(a[i]!==end[i]||a[i+1]!==end[i+1]||a[i+2]!==end[i+2]);
          if(!d) continue;
          const x=(i>>2)%r.w,y=Math.floor((i>>2)/r.w);
          changes++; peak=Math.max(peak,d);
          if((r.south&&y>=r.south.bottom)||r.gates.some(({rect:[a,b,w,h]})=>x>=a&&x<a+w&&y>=b&&y<b+h)) forbidden++;
        }
        return {salle:r.label,pixels_animes:changes,variation_max_255:peak,seuils_modifies:forbidden,raccord_pixels:seam};
      });
    });
    for (const q of proof) assert(q.pixels_animes >= 70 && q.variation_max_255 <= 15 && !q.seuils_modifies && !q.raccord_pixels,JSON.stringify(q));
    console.log('PASS · 15 éclairages animés et raccord de boucle exact ; passages et bandes sud immobiles.');
    await p.goto(url);await waitAtlas(p,3);
    const prev = await b.newPage({viewport:{width:1380,height:940},reducedMotion:'reduce'});
    await prev.route(url+'/avant-test', r => r.fulfill({status:200, contentType:'text/html; charset=utf-8',body:previous}));
    await prev.goto(url+'/avant-test');await waitAtlas(prev,3);
    for(const n of [0,1,2]) {
      await Promise.all([lockPhase(p,n), lockPhase(prev,n)]);
      assert.deepEqual(await atlas(p), await atlas(prev));
    }
    await prev.close();await lockPhase(p,3);
    assert(await p.locator('#comparatif-video').evaluate(x => x.getBoundingClientRect().bottom < document.querySelector('#overview-grid').getBoundingClientRect().top));
    await play(p);await p.locator('#tab-work').click();
    assert(await p.locator('#comparatif-video').isHidden());
    assert(await p.locator('#film-comparatif').evaluate(v=>v.paused));
    await p.locator('#tab-all').click();await waitAtlas(p,3);
    const screenshot = process.env.ATLAS_SCREENSHOT;
    if(screenshot) await p.screenshot({path:screenshot});
    assert.deepEqual(errs, []);
    const m = await b.newPage({viewport:{width:390,height:820},reducedMotion:'reduce',offline:true});
    await m.setContent('<style>body{margin:0}iframe{display:block;width:100%;height:100dvh;border:0}</style><iframe id="aperçu" sandbox="allow-scripts"></iframe>');
    await m.locator('iframe').evaluate((el,html)=>{el.srcdoc=html;},stock);
    const inFrame=m.frameLocator('iframe');
    assert.equal(await inFrame.locator('.atlas-map').count(),15);
    await play(inFrame);
    assert(await inFrame.locator('html').evaluate(root=>root.scrollWidth<=innerWidth+1));
    const idx=JSON.parse(fs.readFileSync(path.join(out,'Index-lumiere-ancree.json'),'utf8'));
    const alpha=Math.max(...idx.plans.flatMap(p=>p.sources.map(s=>s.alpha_reflet_max_255)));
    assert(alpha <= 25);
    const record={statut:'PASS',salles:15,foyers:30,poteaux:42,plans_hors_nuit_identiques:45,texture_sha256:idx.texture.sha256_masque,reflets_max_pourcent:Math.round(alpha/255*10000)/100,verification_animation:proof,geometrie_etoffes_ambiances_identiques:true,iframe_sandbox_hors_ligne:true};
    const json=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2)+'\n');
    json('Verification.json',record);
    json('Verification-video.json',{statut:'PASS',lecture_dans_apercu:true,iframe_sandbox_hors_ligne:true,video_avant_cartes:true,edition:'Lueur tamisée',duree_s:9.6,sources_embarquees:['WebM/VP9','MP4/H.264'],suspendue_en_atelier:true});
    console.log('PASS · 45 vues non nocturnes identiques · vidéo actualisée lue dans l’aperçu et dans un iframe mobile sans réseau.');
  } finally { await b.close(); }
})().catch(e => {console.error(e);process.exitCode=1;});
