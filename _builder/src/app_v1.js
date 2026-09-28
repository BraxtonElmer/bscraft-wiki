/* BSCraft 4 Wiki - app */
(function () {
  const W = window.WIKI;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  /* ---------------- pixel flowers (Minecraft-style, drawn at runtime) ---------------- */
  const STEM = ['....G....', '...GG.L..', '....GLL..', '..LLG....', '...LG....', '....G....'];
  const PAL = { G: '#3F7A34', L: '#6FB04F', W: '#FBF8F0', Y: '#F2C53D', O: '#D99A1E', B: '#5B8DEF', D: '#3A5FC0', R: '#E0453A', K: '#3A2A2A',
    P: '#A764D6', l: '#D6A8F5', p: '#F7B3CF', Q: '#E87FAE', T: '#F08A2C', U: '#FFD24A', V: '#D9542A', S: '#FFD23A', N: '#6B3F1D', M: '#A86A22', w: '#FFFFFF' };
  const FLOWERS = {
    daisy: ['..W.W.W..', '.WWWWWWW.', 'WWWYYYWWW', '.WWYOYWW.', 'WWWYYYWWW', '.WWWWWWW.', '..W.W.W..'],
    cornflower: ['...B.B...', '..BBBBB..', '.BBDBDBB.', '..BBDBB..', '.BBDBDBB.', '..BBBBB..', '...B.B...'],
    poppy: ['.........', '..RRRRR..', '.RRRKRRR.', '.RRKKKRR.', '.RRRKRRR.', '..RRRRR..', '...R.R...'],
    allium: ['..PPPPP..', '.PPlPPPP.', 'PPPPPlPPP', 'PlPPPPPlP', 'PPPPlPPPP', '.PPPPPPP.', '..PPPPP..'],
    petals: ['..pp..pp.', '.pQQp.pQp', '..pp..pp.', '....pp...', '...pQQp..', '....pp...', '.........'],
    torchflower: ['...T.T...', '..TUUUT..', '.TUUVUUT.', '..TUUUT..', '...TTT...', '....T....', '.........'],
    lily: ['...G.....', '..G.G....', '.W...GW..', 'WWW...WW.', '.W....W..', '....GW...', '...WWW...'],
    sunflower: ['..SSSSS..', '.SSMMMSS.', 'SSMNNNMSS', 'SSMNNNMSS', 'SSMNNNMSS', '.SSMMMSS.', '..SSSSS..'],
  };
  function sprite(name, scale = 3) {
    const rows = FLOWERS[name].concat(STEM);
    const c = document.createElement('canvas'); c.width = 9 * scale; c.height = rows.length * scale;
    const g = c.getContext('2d');
    rows.forEach((r, y) => [...r].forEach((ch, x) => { if (PAL[ch]) { g.fillStyle = PAL[ch]; g.fillRect(x * scale, y * scale, scale, scale); } }));
    return c.toDataURL();
  }
  const FL = {}; Object.keys(FLOWERS).forEach(k => FL[k] = sprite(k));
  const groupOf = id => W.groups.find(g => g.id === id);
  const flowerOfPage = slug => FL[groupOf(W.pages[slug].group).flower];
  function vine() {
    const c = document.createElement('canvas'); c.width = 24; c.height = 5; const g = c.getContext('2d');
    const on = (x, y, col) => { g.fillStyle = col; g.fillRect(x, y, 1, 1); };
    for (let x = 0; x < 24; x++) on(x, 2 + (x % 12 < 6 ? 0 : 0), '#6FB04F');
    [[3, 1], [4, 0], [5, 1], [15, 3], [16, 4], [17, 3]].forEach(([x, y]) => on(x, y, '#3F7A34'));
    on(10, 1, '#F7B3CF'); on(10, 3, '#F7B3CF'); on(9, 2, '#F7B3CF'); on(11, 2, '#F7B3CF'); on(10, 2, '#F2C53D');
    on(21, 1, '#D6A8F5'); on(21, 3, '#D6A8F5'); on(20, 2, '#D6A8F5'); on(22, 2, '#D6A8F5'); on(21, 2, '#FBF8F0');
    return c.toDataURL();
  }
  const VINE = vine();
  document.documentElement.style.setProperty('--flower-note', `url(${FL.sunflower})`);
  $('#brandFlower').src = FL.allium;

  /* ---------------- theme ---------------- */
  const root = document.documentElement;
  function effectiveDark() { const t = root.dataset.theme; return t ? t === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; }
  function setThemeIcon() { $('#themeBtn').textContent = effectiveDark() ? '☀' : '☾'; }
  const saved = store.get('bsc-theme'); if (saved) root.dataset.theme = saved;
  setThemeIcon();
  $('#themeBtn').addEventListener('click', () => { const t = effectiveDark() ? 'light' : 'dark'; root.dataset.theme = t; store.set('bsc-theme', t); setThemeIcon(); });
  matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', setThemeIcon);

  /* ---------------- sidebar ---------------- */
  $('#nav').innerHTML = `<div class="grp"><h4><img class="pix" src="${FL.daisy}" alt="">Home</h4><a href="#/" data-r="home">Welcome</a><a href="#/mods" data-r="mods">All ${W.meta.mods} mods</a></div>` +
    W.groups.map(g => `<div class="grp"><h4><img class="pix" src="${FL[g.flower]}" alt="">${esc(g.name)}</h4>` +
      g.pages.map(s => `<a href="#/p/${s}" data-r="p/${s}">${esc(W.pages[s].label)}</a>`).join('') + '</div>').join('');
  const side = $('#side'), menuBtn = $('#menuBtn');
  menuBtn.addEventListener('click', () => { const o = side.classList.toggle('open'); menuBtn.setAttribute('aria-expanded', o); });

  /* ---------------- search ---------------- */
  const q = $('#q'), res = $('#results');
  let sel = -1, hits = [];
  function score(e, t) {
    const title = e.t.toLowerCase();
    if (title === t) return 100;
    if (title.startsWith(t)) return 80 - title.length / 100;
    if (title.includes(t)) return 60 - title.length / 100;
    if ((e.s || '').toLowerCase().includes(t)) return 20;
    return 0;
  }
  function runSearch() {
    const t = q.value.trim().toLowerCase();
    if (t.length < 2) { res.hidden = true; return; }
    const seen = new Set();
    hits = W.search.map(e => [score(e, t), e]).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0])
      .map(x => x[1]).filter(e => { const k = e.t + e.u; if (seen.has(k)) return false; seen.add(k); return true; }).slice(0, 14);
    sel = hits.length ? 0 : -1;
    res.innerHTML = hits.length ? hits.map((e, i) => `<a href="${e.u}${e.q ? (e.u.includes('?') ? '&' : '?') + 'q=' + encodeURIComponent(e.q) : ''}" role="option" aria-selected="${i === sel}"><b>${esc(e.t)}</b><span class="k">${esc(e.k)}</span>${e.s ? `<span class="s">${esc(e.s)}</span>` : ''}</a>`).join('')
      : `<div class="none">Nothing called “${esc(q.value)}” yet. Try a shorter word, or a mod name.</div>`;
    res.hidden = false;
  }
  q.addEventListener('input', runSearch);
  q.addEventListener('keydown', e => {
    const links = $$('a', res);
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault(); if (!links.length) return;
      sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
      links.forEach((a, i) => a.setAttribute('aria-selected', i === sel)); links[sel].scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter' && links[sel]) { location.hash = links[sel].getAttribute('href'); closeSearch(); }
    else if (e.key === 'Escape') closeSearch();
  });
  function closeSearch() { res.hidden = true; q.blur(); }
  res.addEventListener('click', e => { if (e.target.closest('a')) { res.hidden = true; q.value = ''; } });
  document.addEventListener('click', e => { if (!e.target.closest('.searchbox')) res.hidden = true; });
  document.addEventListener('keydown', e => { if (e.key === '/' && document.activeElement !== q && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); q.focus(); } });

  /* ---------------- helpers ---------------- */
  const CAT_COLORS = ['#7C5BD1', '#4F7A45', '#C8506C', '#A87B12', '#3A7FB8', '#B5603A', '#7A5A9A', '#2F8A7A', '#9A4F8A', '#6B7A2F', '#C0763A', '#4F6FA8', '#8A6243', '#5E5173', '#A0A0B8'];
  const catColor = c => CAT_COLORS[Math.max(0, W.cats.indexOf(c)) % CAT_COLORS.length];
  function logoHTML(m, big) {
    return m.logo ? `<span class="logo"><img src="assets/logos/${m.id}.png" alt="" loading="lazy"></span>`
      : `<span class="logo mono" style="--c:${catColor(m.cat)}">${esc(m.name.replace(/^[^A-Za-z]+/, '').charAt(0).toUpperCase())}</span>`;
  }
  const modById = Object.fromEntries(W.mods.map(m => [m.id, m]));
  function toast(msg) { const t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); t.textContent = msg; document.body.append(t); setTimeout(() => t.remove(), 1800); }
  const foot = () => `<footer class="foot"><div><b>BSCraft 4 Wiki</b><br>Built from the pack's own files: recipes, loot tables, configs and mod code, cross-checked with the mods' wikis.</div><div>Item icons and mod logos belong to their mods' authors.<br>Minecraft ${W.meta.mc} · Forge ${W.meta.forge} · ${W.meta.mods} mods</div></footer>`;

  /* ---------------- home ---------------- */
  function home() {
    const splash = W.splashes[Math.floor(Math.random() * W.splashes.length)];
    const start = [['quality-of-life', 'Start with this', true], ['what-is-bscraft', 'The big picture'], ['controls', 'Keys and tools'], ['settings', 'Make it run nicely']];
    const bosses = W.bosses.slice().sort((a, b) => ({ S: 0, A: 1, B: 2, C: 3 }[a.tier] ?? 4) - ({ S: 0, A: 1, B: 2, C: 3 }[b.tier] ?? 4));
    return `<section class="hero" aria-label="Welcome">
      <canvas id="meadow" aria-hidden="true"></canvas>
      <div class="inner">
        <div class="eyebrow"><span>Minecraft ${W.meta.mc}</span><span>Forge ${W.meta.forge}</span><span>${W.meta.mods} mods</span></div>
        <div class="titlewrap"><h1>BSCraft <em>4</em></h1><div class="splash">${esc(splash)}</div></div>
        <p class="sub">A field guide to the whole pack: every biome, boss, blade, spell and comfort we could find.</p>
        <div class="serverchip"><code>${esc(W.meta.server)}</code><button type="button" id="copyIp">Copy address</button></div>
      </div>
    </section>
    <section class="band"><header><div><h2>Start here</h2><p class="lead">It's a map, not a route. These four pages make everything else easier.</p></div></header>
      <div class="start-grid">${start.map(([s, tag, star]) => `<a class="sprout${star ? ' star' : ''}" href="#/p/${s}"><span class="tag">${tag}</span><b>${esc(W.pages[s].label)}</b><span>${esc(W.pages[s].lede.slice(0, 110))}…</span></a>`).join('')}</div>
    </section>
    <section class="band twocol">
      <div class="panel"><h3>The comforts that matter most</h3>${W.qol}</div>
      <div class="panel"><h3>Best in slot, at a glance</h3>${W.bis}</div>
    </section>
    <section class="band"><header><div><h2>Wander the wiki</h2><p class="lead">Every page, planted by what you're after.</p></div><a href="#/mods">Browse all ${W.meta.mods} mods →</a></header>
      <div class="garden">${W.groups.map(g => `<div class="bed"><img class="pix" src="${FL[g.flower]}" alt=""><b>${esc(g.name)}</b><p>${esc(g.blurb)}</p><div class="links">${g.pages.map(s => `<a href="#/p/${s}">${esc(W.pages[s].label)}</a>`).join('')}</div></div>`).join('')}</div>
    </section>
    <section class="band"><header><div><h2>Bosses worth the trip</h2><p class="lead">${W.bosses.length} of them, from a 30 HP magnet to a 6,000 HP copy of you.</p></div><a href="#/p/bosses">Full boss table →</a></header>
      <div class="bosses">${bosses.map(b => `<a class="bosscard" href="#/p/bosses?q=${encodeURIComponent(b.name)}"><span class="portrait"><img src="images/bosses/${b.slug}.png" alt="" loading="lazy" onerror="this.remove()"><span class="ph">${esc(b.name.charAt(0))}</span></span><b>${esc(b.name)}</b><small>${esc(b.hp)} HP${b.tier ? ' · Tier ' + b.tier : ''}</small></a>`).join('')}</div>
    </section>` + foot();
  }

  /* meadow: pixel flowers swaying, petals by day and fireflies by night */
  let raf = 0;
  function meadow() {
    cancelAnimationFrame(raf);
    const cv = $('#meadow'); if (!cv) return;
    const g = cv.getContext('2d'); const dpr = Math.min(2, devicePixelRatio || 1);
    const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const px = 4; let w, h, plants = [], motes = [];
    const names = Object.keys(FLOWERS);
    function size() {
      const r = cv.getBoundingClientRect(); w = r.width; h = r.height; cv.width = w * dpr; cv.height = h * dpr; g.setTransform(dpr, 0, 0, dpr, 0, 0); g.imageSmoothingEnabled = false;
      plants = []; const n = Math.floor(w / 30);
      for (let i = 0; i < n; i++) plants.push({ x: Math.random() * w, k: names[Math.floor(Math.random() * names.length)], s: 0.7 + Math.random() * 0.55, ph: Math.random() * 6.28, near: Math.random() < 0.5 });
      plants.sort((a, b) => a.near - b.near || a.s - b.s);
      motes = Array.from({ length: 26 }, () => ({ x: Math.random() * w, y: Math.random() * h * 0.8, v: 0.15 + Math.random() * 0.35, ph: Math.random() * 6.28 }));
    }
    function drawFlower(p, t) {
      const rows = FLOWERS[p.k].concat(STEM); const sc = px * p.s; const baseY = h - 26 - (p.near ? 0 : 16);
      const sway = still ? 0 : Math.sin(t / 1400 + p.ph) * 1.6;
      rows.forEach((r, y) => {
        const lean = Math.round(sway * (1 - y / rows.length));
        [...r].forEach((ch, x) => { if (PAL[ch]) { g.fillStyle = PAL[ch]; g.fillRect(Math.round(p.x + (x + lean) * sc), Math.round(baseY - (rows.length - y) * sc), Math.ceil(sc), Math.ceil(sc)); } });
      });
    }
    function frame(t) {
      const dark = effectiveDark();
      g.clearRect(0, 0, w, h);
      if (dark) { g.fillStyle = 'rgba(255,255,255,.7)'; for (let i = 0; i < 40; i++) { const sx = (i * 97.3) % w, sy = (i * 53.7) % (h * 0.55); const tw = still ? 1 : 0.5 + 0.5 * Math.sin(t / 700 + i); g.globalAlpha = 0.25 + tw * 0.5; g.fillRect(sx, sy, 2, 2); } g.globalAlpha = 1; }
      plants.filter(p => !p.near).forEach(p => drawFlower(p, t));
      const cs = getComputedStyle(root);
      g.fillStyle = cs.getPropertyValue('--grass-2'); g.fillRect(0, h - 42, w, 42);
      g.fillStyle = cs.getPropertyValue('--grass-1'); for (let x = 0; x < w; x += 8) g.fillRect(x, h - 44 - ((x * 7) % 3) * 2, 8, 10);
      g.fillStyle = cs.getPropertyValue('--soil'); g.fillRect(0, h - 16, w, 16);
      plants.filter(p => p.near).forEach(p => drawFlower(p, t));
      motes.forEach((m, i) => {
        if (!still) { m.x += dark ? Math.sin(t / 900 + m.ph) * 0.4 : m.v; m.y += dark ? Math.cos(t / 1100 + m.ph) * 0.3 : m.v * 0.45; if (m.x > w) m.x = -4; if (m.y > h - 40) m.y = 0; }
        if (dark) { const a = 0.35 + 0.65 * Math.abs(Math.sin(t / 600 + m.ph)); g.fillStyle = `rgba(214,255,120,${a})`; g.shadowColor = '#d6ff78'; g.shadowBlur = 10; g.fillRect(m.x, m.y, 3, 3); g.shadowBlur = 0; }
        else { g.fillStyle = i % 3 ? '#F7B3CF' : '#E87FAE'; g.fillRect(m.x, m.y, 4, 3); }
      });
      if (!still) raf = requestAnimationFrame(frame);
    }
    size(); addEventListener('resize', size, { passive: true }); raf = requestAnimationFrame(frame);
  }

  /* ---------------- guide page ---------------- */
  function page(slug, anchor, params) {
    const p = W.pages[slug]; if (!p) return notFound();
    const g = groupOf(p.group);
    const all = W.groups.flatMap(x => x.pages); const i = all.indexOf(slug);
    const prev = all[i - 1], next = all[i + 1];
    const html = `<div class="page" style="--flower:url(${FL[g.flower]})"><article>
      <div class="crumbs"><img class="pix" src="${FL[g.flower]}" alt=""><a href="#/p/${g.pages[0]}">${esc(g.name)}</a><span>›</span><span>${esc(p.label)}</span></div>
      <h1>${esc(p.title)}</h1><div class="vine" style="background-image:url(${VINE})"></div>
      <div class="body">${p.html}</div>
      <nav class="pager" aria-label="Next and previous pages">${prev ? `<a href="#/p/${prev}"><small>← Previous</small><b>${esc(W.pages[prev].label)}</b></a>` : '<span></span>'}${next ? `<a class="next" href="#/p/${next}"><small>Next →</small><b>${esc(W.pages[next].label)}</b></a>` : ''}</nav>
      ${foot()}</article>
      ${p.toc.length > 1 ? `<aside class="toc" aria-label="On this page"><h5>On this page</h5>${p.toc.map(t => `<a href="#/p/${slug}/${t.id}" data-id="${t.id}">${esc(t.t)}</a>`).join('')}</aside>` : ''}</div>`;
    return { html, after() { setupTables(params.get('q')); setupTips(); setupToc(); if (anchor) { const el = document.getElementById(anchor); if (el) el.scrollIntoView(); } } };
  }

  function setupTables(prefill) {
    $$('table.db').forEach(t => {
      const tools = t.closest('.tablewrap').previousElementSibling; const inp = $('input[data-filter]', tools), count = $('[data-count]', tools);
      const rows = [...t.tBodies[0].rows];
      const apply = () => { const s = inp.value.trim().toLowerCase(); let n = 0; rows.forEach(r => { const hit = !s || r.textContent.toLowerCase().includes(s) || (s.length === 1 && r.cells[r.cells.length - 1].textContent.trim().toLowerCase() === s); r.classList.toggle('hide', !hit); if (hit) n++; }); count.textContent = `${n} of ${rows.length}`; };
      inp.addEventListener('input', apply); if (prefill) inp.value = prefill; apply();
      $$('th', t).forEach((th, ci) => {
        th.tabIndex = 0;
        const go = () => {
          const dir = th.classList.contains('asc') ? -1 : 1; $$('th', t).forEach(x => x.classList.remove('asc', 'desc')); th.classList.add(dir === 1 ? 'asc' : 'desc');
          const val = r => { const v = r.cells[ci].textContent.trim(); const n = parseFloat(v.replace(/[^0-9.\-]/g, '')); if (ci === r.cells.length - 1) return { S: 0, A: 1, B: 2, C: 3 }[v] ?? 9; return /^(about )?-?[0-9]/.test(v) && !isNaN(n) ? n : v.toLowerCase(); };
          rows.sort((a, b) => { const x = val(a), y = val(b); if (typeof x === 'number' && typeof y === 'number') return (x - y) * dir; if (typeof x === 'number') return -1; if (typeof y === 'number') return 1; return x < y ? -dir : x > y ? dir : 0; });
          rows.forEach(r => t.tBodies[0].appendChild(r));
        };
        th.addEventListener('click', go); th.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
      });
    });
  }

  /* Minecraft-style tooltip on database rows */
  const tip = $('#tip');
  function setupTips() {
    $$('table.db').forEach(t => {
      const heads = $$('th', t).map(th => th.textContent.trim());
      $$('tbody tr', t).forEach(r => {
        const cell = r.cells[0];
        cell.addEventListener('mouseenter', () => {
          const get = n => { const i = heads.indexOf(n); return i >= 0 ? r.cells[i].textContent.trim() : ''; };
          const tier = get('Tier'); const name = cell.textContent.trim(); const from = r.cells[1].textContent.trim();
          let lines = '';
          if (heads.includes('DPS')) lines = `<div class="g">When in Main Hand:</div><div class="v"> ${esc(get('Dmg'))} Attack Damage</div><div class="v"> ${esc(get('Speed'))} Attack Speed</div>`;
          else if (heads.includes('Tough.')) lines = `<div class="g">When worn as a full set:</div><div class="b">+${esc(get('Armor'))} Armor</div><div class="b">+${esc(get('Tough.'))} Armor Toughness per piece</div>` + (get('KB res') !== '0' && get('KB res') !== '-' ? `<div class="b">+${esc(get('KB res'))} Knockback Resistance</div>` : '');
          else lines = `<div class="g">Boss</div><div class="v"> ${esc(get('HP'))} Health</div>` + (get('Armor') !== '-' ? `<div class="b"> ${esc(get('Armor'))} Armor</div>` : '');
          tip.innerHTML = `<div class="t ${tier ? 't' + tier : ''}">${esc(name)}</div>${lines}<div class="m">${esc(from.split(',')[0])}</div>`;
          tip.hidden = false;
        });
        cell.addEventListener('mousemove', e => { const x = Math.min(innerWidth - tip.offsetWidth - 12, e.clientX + 16); tip.style.left = x + 'px'; tip.style.top = Math.min(innerHeight - tip.offsetHeight - 12, e.clientY + 14) + 'px'; });
        cell.addEventListener('mouseleave', () => { tip.hidden = true; });
      });
    });
  }

  let tocObs;
  function setupToc() {
    tocObs?.disconnect(); const links = $$('.toc a'); if (!links.length) return;
    tocObs = new IntersectionObserver(es => { es.forEach(e => { if (e.isIntersecting) links.forEach(a => a.classList.toggle('on', a.dataset.id === e.target.id)); }); }, { rootMargin: '-80px 0px -70% 0px' });
    $$('article h2[id]').forEach(h => tocObs.observe(h));
  }

  /* ---------------- mods ---------------- */
  function modsPage(params) {
    const cat = params.get('c') || '';
    const counts = {}; W.mods.forEach(m => counts[m.cat] = (counts[m.cat] || 0) + 1);
    const html = `<article><div class="crumbs"><img class="pix" src="${FL.sunflower}" alt=""><span>Reference</span></div>
      <h1>All ${W.meta.mods} mods</h1><div class="vine" style="background-image:url(${VINE})"></div>
      <div class="body"><p>Every mod in the pack, grouped by what it does for you. Pick one to see what it adds and every place this wiki talks about it.</p></div>
      <div class="dbtools"><label class="filter"><span>Filter</span><input id="modfilter" type="search" placeholder="Name or what it does…"></label><span class="count" id="modcount"></span></div>
      <div class="chips" role="group" aria-label="Categories"><button class="chip" type="button" data-c="" aria-pressed="${!cat}">Everything<i>${W.mods.length}</i></button>${W.cats.filter(c => counts[c]).map(c => `<button class="chip" type="button" data-c="${esc(c)}" aria-pressed="${cat === c}">${esc(c)}<i>${counts[c]}</i></button>`).join('')}</div>
      <div class="modgrid" id="modgrid"></div>${foot()}</article>`;
    return { html, after() {
      let cur = cat; const inp = $('#modfilter');
      const draw = () => {
        const s = inp.value.trim().toLowerCase();
        const list = W.mods.filter(m => (!cur || m.cat === cur) && (!s || (m.name + ' ' + m.d).toLowerCase().includes(s)));
        $('#modcount').textContent = `${list.length} shown`;
        $('#modgrid').innerHTML = list.map(m => `<a class="modcard" href="#/mod/${m.id}">${logoHTML(m)}<div><b>${esc(m.name)}</b><span>${esc(m.d)}</span></div></a>`).join('');
      };
      inp.addEventListener('input', draw);
      $$('.chip').forEach(b => b.addEventListener('click', () => { cur = b.dataset.c; $$('.chip').forEach(x => x.setAttribute('aria-pressed', x === b)); draw(); }));
      draw();
    } };
  }
  function modPage(id) {
    const m = modById[id]; if (!m) return notFound();
    const html = `<article><div class="crumbs"><img class="pix" src="${FL.sunflower}" alt=""><a href="#/mods">All mods</a><span>›</span><span>${esc(m.cat)}</span></div>
      <div class="modhead">${logoHTML(m, true)}<div><h1>${esc(m.name)}</h1><span class="catchip">${esc(m.cat)}</span></div></div>
      <div class="body"><p style="font-size:18px">${esc(m.d)}</p>
      <p class="jar">${esc(m.jar)}</p>
      ${m.wiki ? `<p><a class="btn" href="${esc(m.wiki)}" target="_blank" rel="noopener">Read the ${esc(m.name)} wiki ↗</a></p>` : ''}
      ${m.m.length ? `<h2 id="in-this-wiki">Where this wiki mentions it</h2><ul class="mentions">${m.m.map(x => `<li><a class="where" href="#/p/${x.p}${x.a ? '/' + x.a : ''}">${esc(W.pages[x.p].label)}${x.at ? ' › ' + esc(x.at) : ''}</a><p>${esc(x.s)}</p></li>`).join('')}</ul>`
        : `<aside class="note">This one works in the background, so the guide doesn't cover it on its own page.</aside>`}
      </div>${foot()}</article>`;
    return { html, after() {} };
  }
  function notFound() { return { html: `<article><h1>Nothing grows here</h1><p>That page doesn't exist. Try the search at the top, or <a href="#/">go back to the start</a>.</p></article>`, after() {} }; }

  /* ---------------- router ---------------- */
  function route() {
    const h = location.hash.replace(/^#\/?/, '');
    const [pathPart, qs] = h.split('?'); const params = new URLSearchParams(qs || '');
    const parts = pathPart.split('/').filter(Boolean);
    let view, key;
    if (!parts.length) { view = { html: home(), after: () => { meadow(); $('#copyIp')?.addEventListener('click', () => { navigator.clipboard?.writeText(W.meta.server).then(() => toast('Copied the server address')).catch(() => toast(W.meta.server)); }); } }; key = 'home'; }
    else if (parts[0] === 'p') { view = page(parts[1], parts[2], params); key = 'p/' + parts[1]; }
    else if (parts[0] === 'mods') { view = modsPage(params); key = 'mods'; }
    else if (parts[0] === 'mod') { view = modPage(parts[1]); key = 'mods'; }
    else { view = notFound(); key = ''; }
    cancelAnimationFrame(raf); tip.hidden = true;
    const main = $('#main'); main.innerHTML = view.html;
    $$('#nav a').forEach(a => a.classList.toggle('on', a.dataset.r === key));
    side.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false');
    if (!parts[2]) scrollTo(0, 0);
    view.after();
    document.title = key === 'home' ? 'BSCraft 4 Wiki' : `${main.querySelector('h1')?.textContent || 'BSCraft 4'} · BSCraft 4 Wiki`;
  }
  addEventListener('hashchange', route);
  route();
})();
