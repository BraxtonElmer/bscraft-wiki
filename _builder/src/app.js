/* BSCraft 4 Wiki */
(function () {
  const W = window.WIKI;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  const groupOf = id => W.groups.find(g => g.id === id);
  const modById = Object.fromEntries(W.mods.map(m => [m.id, m]));

  const ic = k => k ? `<i class="ico i-${k}" aria-hidden="true"></i>` : '';
  const slot = (k, sm) => `<span class="slot${sm ? ' sm' : ''}" aria-hidden="true">${ic(k)}</span>`;

  /* ---------- sidebar ---------- */
  const side = $('#side'), menuBtn = $('#menuBtn');
  const refIcon = groupOf('reference').icon;
  side.innerHTML = `<section><h2>Wiki</h2><ul><li><a href="#/" data-r="home">${ic(groupOf('start').icon)}Home</a></li><li><a href="#/mods" data-r="mods">${ic(refIcon)}All ${W.meta.mods} mods</a></li></ul></section>` +
    W.groups.map(g => `<section><h2>${esc(g.name)}</h2><ul>${g.pages.map(s => `<li><a href="#/p/${s}" data-r="p/${s}">${ic(W.pages[s].icon)}${esc(W.pages[s].label)}</a></li>`).join('')}</ul></section>`).join('');
  menuBtn.addEventListener('click', () => { const o = side.classList.toggle('open'); menuBtn.setAttribute('aria-expanded', o); });

  /* ---------- download menu in the top bar ---------- */
  const dlBtn = $('#dlBtn'), dlMenu = $('#dlmenu');
  const showDl = open => { dlMenu.hidden = !open; dlBtn.setAttribute('aria-expanded', open); };
  dlBtn.addEventListener('click', () => showDl(dlMenu.hidden));
  document.addEventListener('click', e => { if (!e.target.closest('.dlwrap')) showDl(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !dlMenu.hidden) { showDl(false); dlBtn.focus(); } });

  /* ---------- search ---------- */
  const q = $('#q'), res = $('#results');
  let sel = -1;
  const score = (e, t) => { const s = e.t.toLowerCase(); return s === t ? 100 : s.startsWith(t) ? 80 - s.length / 100 : s.includes(t) ? 60 - s.length / 100 : (e.s || '').toLowerCase().includes(t) ? 20 : 0; };
  function show(open) { res.hidden = !open; q.setAttribute('aria-expanded', open); }
  function runSearch() {
    const t = q.value.trim().toLowerCase();
    if (t.length < 2) return show(false);
    const seen = new Set();
    const hits = W.search.map(e => [score(e, t), e]).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]).map(x => x[1])
      .filter(e => { const k = e.t + e.u; if (seen.has(k)) return false; seen.add(k); return true; }).slice(0, 12);
    sel = hits.length ? 0 : -1;
    res.innerHTML = hits.length ? hits.map((e, i) => `<li><a id="r${i}" role="option" aria-selected="${i === sel}" href="${e.u}${e.q ? '?q=' + encodeURIComponent(e.q) : ''}"><b>${esc(e.t)}</b><span class="k">${esc(e.k)}</span>${e.s ? `<span class="s">${esc(e.s)}</span>` : ''}</a></li>`).join('')
      : `<li class="none">No matches for “${esc(q.value)}”. Try one word, or a mod name.</li>`;
    show(true);
  }
  q.addEventListener('input', runSearch);
  q.addEventListener('keydown', e => {
    const links = $$('a', res);
    if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && links.length) {
      e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
      links.forEach((a, i) => a.setAttribute('aria-selected', i === sel)); links[sel].scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter' && links[sel]) { location.hash = links[sel].getAttribute('href'); q.value = ''; show(false); q.blur(); }
    else if (e.key === 'Escape') { show(false); q.blur(); }
  });
  res.addEventListener('click', e => { if (e.target.closest('a')) { q.value = ''; show(false); } });
  document.addEventListener('click', e => { if (!e.target.closest('.searchbox')) show(false); });
  document.addEventListener('keydown', e => { if (e.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName)) { e.preventDefault(); q.focus(); } });

  /* ---------- shared bits ---------- */
  const logo = m => m.logo ? `<span class="logo"><img src="assets/logos/${m.id}.png" alt="" loading="lazy"></span>`
    : `<span class="logo mono" aria-hidden="true">${esc(m.name.replace(/^[^A-Za-z]+/, '').charAt(0).toUpperCase())}</span>`;
  const foot = () => `<footer class="foot"><span>BSCraft 4 Wiki. Built from the pack's own files and checked against the mods' wikis.</span><span><a href="#/p/changelog">What changed in 4.1</a> · Item icons and mod logos belong to their mods' authors. Background art is from the pack's main menu theme.</span></footer>`;

  // page banner: a slice of the title-screen garden (a different corner per part of the wiki), crumbs, and the title with its item
  const banner = (group, crumbs, title, badge) => `<header class="banner g-${group}">
      <nav class="crumbs" aria-label="Breadcrumb"><ol>${crumbs}</ol></nav>
      <div class="titleline">${badge}<h1>${esc(title)}</h1></div></header><div class="titlerule" aria-hidden="true"></div>`;

  /* ---------- tips, shown in the menu's dialogue box ---------- */
  const TIPS = [
    ['Every chest that came with the world has its own loot for each player. A dungeon someone else already emptied still has yours waiting.', 'quality-of-life'],
    ['When you die, everything you carried goes into a corpse. It never despawns while it holds items, and lava doesn\'t destroy it.', 'quality-of-life'],
    ['Anyone can open a corpse, and PvP is on on the server. Go back for your gear soon.', 'quality-of-life'],
    ['Teleporting between waystones you\'ve found is free. Only the warp button in your inventory and warps to another dimension cost anything.', 'quality-of-life'],
    ['After you respawn, log in or change dimension you get up to 50 seconds of protection from damage. Fall damage still counts.', 'quality-of-life'],
    ['Hover an item and press R to see how to make it, or U to see what it\'s used for. When a wiki and JEI disagree, JEI is right.', 'controls'],
    ['Sleeping bags skip the night without moving your spawn point. Hammocks skip the day.', 'quality-of-life'],
    ['Loot chests can\'t be broken by accident. Sneak to break one, and know that it deletes your loot inside.', 'quality-of-life'],
    ['Dungeon spawners shut off after a while. A redstone signal keeps one running if you want a mob farm.', 'quality-of-life'],
    ['Most aircraft recipes are changed in this pack. Check JEI, not the wikis.', 'space-and-vehicles'],
    ['Chunk loaders keep farms running, but they switch off after 7 days offline.', 'quality-of-life'],
    ['Dragon eggs don\'t spawn in chests here. Hatch one near lava for a fire dragon, underwater for water, or in snow for ice.', 'mounts'],
  ];
  let typing;
  function tips() {
    const box = $('#tip'); if (!box) return;
    const line = $('.line', box), typed = $('.typed', box), said = $('.said', box), count = $('.who span', box), more = $('#tipMore');
    const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let i = Math.floor(Math.random() * TIPS.length);
    const show = () => {
      clearInterval(typing);
      const [text, slug] = TIPS[i];
      said.textContent = text; count.textContent = `${i + 1} of ${TIPS.length}`;
      more.href = `#/p/${slug}`; more.textContent = `Read: ${W.pages[slug].label}`;
      line.classList.remove('done');
      if (still) { typed.textContent = text; line.classList.add('done'); return; }
      let n = 0; typed.textContent = '';
      typing = setInterval(() => { n += 2; typed.textContent = text.slice(0, n); if (n >= text.length) { clearInterval(typing); line.classList.add('done'); } }, 22);
    };
    line.addEventListener('click', () => { clearInterval(typing); typed.textContent = TIPS[i][0]; line.classList.add('done'); });
    $('#tipNext').addEventListener('click', () => { i = (i + 1) % TIPS.length; show(); });
    show();
  }

  /* ---------- home: laid out like the pack's title screen ---------- */
  function home() {
    const start = [['quality-of-life', 'Per-player loot, keeping your items when you die, free travel, and the rest.'],
      ['what-is-bscraft', 'The pack in a few paragraphs, and the best gear at a glance.'],
      ['controls', 'Every key that matters, including the magic ones.'],
      ['settings', 'FOV, shaders and the settings most people change.']];
    const html = `<div class="home">
      <header class="hero">
        <div class="titleblock">
          <h1><img src="assets/theme/logo.png" alt="BSCraft 4 Wiki" width="254" height="73"></h1>
        </div>
        <nav class="heromenu" aria-label="Main menu"><a href="#/p/what-is-bscraft">About</a><a href="#/p/bosses">Bosses</a><a href="#/p/magic">Magic</a><a href="#/mods">Mods</a></nav>
      </header>
      <section class="panel getpack" aria-labelledby="h-get">
        <h2 id="h-get">Get the pack</h2>
        <p class="sub">The launcher installs BSCraft 4 and keeps it up to date. Minecraft 1.20.1 on Forge ${W.meta.forge}, ${W.meta.mods} mods.</p>
        <div class="linkrow">
          <a class="btn primary dl" href="https://bscraft.zukashix.com/launcher/bsclauncher-setup.exe"><b>Windows</b><small>bsclauncher-setup.exe</small></a>
          <a class="btn dl" href="https://bscraft.zukashix.com/launcher/bsclauncher-macos.dmg"><b>macOS</b><small>bsclauncher-macos.dmg</small></a>
        </div>
      </section>
      <section class="dialogue" id="tip" aria-label="Tips">
        <div class="portrait"><img src="assets/theme/portrait.png" alt="" width="60" height="60"></div>
        <div class="say">
          <p class="who">Tip <span></span></p>
          <p class="line"><span class="sr-only said" aria-live="polite"></span><span class="typed" aria-hidden="true"></span></p>
          <div class="acts"><button class="dbtn" type="button" id="tipNext">Next tip</button><a class="dbtn" id="tipMore" href="#/p/quality-of-life">Read more</a></div>
        </div>
      </section>
      <section aria-labelledby="h-start"><h2 id="h-start">Start here</h2><p class="sub">It's a map, not a route. These four pages make the rest easier, and there is more out there than any page covers.</p>
        <ul class="startlist">${start.map(([s, d]) => `<li><a href="#/p/${s}">${slot(W.pages[s].icon)}<b>${esc(W.pages[s].label)}</b><span class="d">${esc(d)}</span></a></li>`).join('')}</ul>
      </section>
      <section class="panel contentsbox" aria-labelledby="h-contents"><h2 id="h-contents">Contents</h2>
        <p class="lede">${esc(W.intro)} Or browse <a href="#/mods">all ${W.meta.mods} mods</a>.</p>
        <div class="contents">${W.groups.map(g => `<section><h3>${slot(g.icon, 1)}${esc(g.name)}</h3><p>${esc(g.blurb)}</p><ol>${g.pages.map(s => `<li><a href="#/p/${s}">${ic(W.pages[s].icon)}${esc(W.pages[s].label)}</a></li>`).join('')}</ol></section>`).join('')}</div>
      </section>
      <div class="glance">
        <section class="panel" aria-labelledby="h-qol"><img class="art" src="assets/theme/items_azure_flower.png" alt="" width="130" height="154"><h2 id="h-qol">The comforts that matter most</h2>${W.qol}</section>
        <section class="panel" aria-labelledby="h-bis"><img class="art" src="assets/theme/items_hero_sword.png" alt="" width="130" height="154"><h2 id="h-bis">Best in slot</h2>${W.bis}</section>
      </div>
      ${foot()}</div>`;
    return { html, title: 'BSCraft 4 Wiki', after() { tips(); hero(); } };
  }

  /* ---------- guide page ---------- */
  function page(slug, anchor, params) {
    const p = W.pages[slug]; if (!p) return notFound();
    const g = groupOf(p.group), all = W.groups.flatMap(x => x.pages), i = all.indexOf(slug);
    const prev = all[i - 1], next = all[i + 1];
    const wide = p.html.includes('<table class="db"');
    const html = `<div class="page${wide ? ' wide' : ''}"><article class="leaf">
      ${banner(g.id, `<li><a href="#/">Wiki</a></li><li><a href="#/p/${g.pages[0]}">${esc(g.name)}</a></li><li aria-current="page">${esc(p.label)}</li>`, p.title, slot(p.icon))}
      ${p.about.length ? `<section class="about" aria-label="About this page">${p.about.map((t, i) => `<p${i ? '' : ' class="lede"'}>${esc(t)}</p>`).join('')}${p.how ? `<p class="how"><b>Reading the table:</b> ${esc(p.how)}</p>` : ''}</section>` : ''}
      ${p.html}
      ${p.read.length ? `<aside class="further" aria-labelledby="fr-${slug}"><h2 id="fr-${slug}">Further reading</h2><ul>${p.read.map(r => `<li><a href="${esc(r.u)}" target="_blank" rel="noopener">${esc(r.name)}</a><span>${esc(r.k)}</span><a class="inwiki" href="#/mod/${r.id}">In this wiki</a></li>`).join('')}</ul></aside>` : ''}
      ${p.credits && p.credits.length ? `<p class="credits">Pictures on this page: ${p.credits.map(c => `<a href="${esc(c.u)}" target="_blank" rel="noopener">${esc(c.t)}</a> (${esc(c.w)})`).join(', ')}.</p>` : ''}
      <nav class="pager" aria-label="Previous and next page">${prev ? `<a href="#/p/${prev}" rel="prev">${slot(W.pages[prev].icon)}<small>Previous</small><b>${esc(W.pages[prev].label)}</b></a>` : ''}${next ? `<a class="next" href="#/p/${next}" rel="next">${slot(W.pages[next].icon)}<small>Next</small><b>${esc(W.pages[next].label)}</b></a>` : ''}</nav>
      ${foot()}</article>
      ${p.toc.length > 1 ? `<nav class="toc" aria-labelledby="toc-h"><h2 id="toc-h">On this page</h2><ol>${p.toc.map(t => `<li><a href="#/p/${slug}/${t.id}" data-id="${t.id}">${esc(t.t)}</a></li>`).join('')}</ol></nav>` : ''}</div>`;
    return { html, title: p.title, after() { tables(params.get('q')); tocSpy(); if (anchor) document.getElementById(anchor)?.scrollIntoView(); } };
  }

  function tables(prefill) {
    $$('table.db').forEach(t => {
      const box = t.closest('.tablewrap').previousElementSibling, inp = $('input', box), out = $('output', box);
      const rows = [...t.tBodies[0].rows];
      const apply = () => { const s = inp.value.trim().toLowerCase(); let n = 0; rows.forEach(r => { const hit = !s || r.textContent.toLowerCase().includes(s); r.hidden = !hit; n += hit; }); out.textContent = `${n} of ${rows.length}`; };
      inp.addEventListener('input', apply); if (prefill) inp.value = prefill; apply();
      const labels = $$('thead th', t).map(th => th.textContent.trim());   // shown beside each number when the table becomes cards
      rows.forEach(r => [...r.cells].forEach((c, i) => { if (c.classList.contains('n')) c.dataset.label = labels[i]; }));
      $$('thead th', t).forEach((th, ci) => {
        const b = document.createElement('button'); b.type = 'button'; b.textContent = th.textContent; th.textContent = ''; th.append(b);
        b.addEventListener('click', () => {
          const dir = th.getAttribute('aria-sort') === 'ascending' ? -1 : 1;
          $$('thead th', t).forEach(x => x.removeAttribute('aria-sort')); th.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
          const tierCol = ci === t.rows[0].cells.length - 1;
          const val = r => { const v = r.cells[ci].textContent.trim(); if (tierCol) return { S: 0, A: 1, B: 2, C: 3 }[v] ?? 9; const n = parseFloat(v.replace(/[^0-9.\-]/g, '')); return /^(about )?-?[0-9]/.test(v) && !isNaN(n) ? n : v.toLowerCase(); };
          rows.sort((a, c) => { const x = val(a), y = val(c); if (typeof x === 'number' && typeof y === 'number') return (x - y) * dir; if (typeof x === 'number') return -1; if (typeof y === 'number') return 1; return x < y ? -dir : x > y ? dir : 0; });
          rows.forEach(r => t.tBodies[0].append(r));
        });
      });
    });
  }

  let spy;
  function tocSpy() {
    spy?.disconnect(); const links = $$('.toc a'); if (!links.length) return;
    spy = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) links.forEach(a => a.classList.toggle('on', a.dataset.id === e.target.id)); }), { rootMargin: '-70px 0px -70% 0px' });
    $$('article h2[id]').forEach(h => spy.observe(h));
  }

  /* ---------- mods ---------- */
  function modsPage(params) {
    const counts = {}; W.mods.forEach(m => counts[m.cat] = (counts[m.cat] || 0) + 1);
    const html = `<div class="page"><article class="leaf">
      ${banner('reference', `<li><a href="#/">Wiki</a></li><li aria-current="page">Mods</li>`, `All ${W.meta.mods} mods`, slot(refIcon))}
      <p class="lede">Every mod in the pack. Open one to see what it adds and every place this wiki mentions it.</p>
      <div class="tabletools"><label for="modq">Filter</label><input id="modq" type="search" placeholder="Name or what it does">
        <label for="modcat">Category</label><select id="modcat"><option value="">All categories</option>${W.cats.filter(c => counts[c]).map(c => `<option${params.get('c') === c ? ' selected' : ''}>${esc(c)}</option>`).join('')}</select>
        <output id="modn" for="modq modcat"></output></div>
      <ul class="modlist" id="modlist"></ul>${foot()}</article></div>`;
    return { html, title: 'All mods', after() {
      const inp = $('#modq'), cat = $('#modcat');
      const draw = () => {
        const s = inp.value.trim().toLowerCase(), c = cat.value;
        const list = W.mods.filter(m => (!c || m.cat === c) && (!s || (m.name + ' ' + m.d).toLowerCase().includes(s)));
        $('#modn').textContent = `${list.length} shown`;
        $('#modlist').innerHTML = list.map(m => `<li><a href="#/mod/${m.id}">${logo(m)}<span><b>${esc(m.name)}</b><span class="d">${esc(m.d)}</span></span><span class="cat">${esc(m.cat)}</span></a></li>`).join('');
      };
      inp.addEventListener('input', draw); cat.addEventListener('change', draw); draw();
    } };
  }
  function modPage(id) {
    const m = modById[id]; if (!m) return notFound();
    const html = `<div class="page"><article class="leaf">
      ${banner('reference', `<li><a href="#/">Wiki</a></li><li><a href="#/mods">Mods</a></li><li aria-current="page">${esc(m.name)}</li>`, m.name, logo(m))}
      <p class="lede">${esc(m.d)}</p>
      <div class="linkrow">${m.wiki ? `<a class="btn primary" href="${esc(m.wiki)}" target="_blank" rel="noopener">Official wiki</a>` : ''}${m.links.map(([k, u]) => `<a class="btn" href="${esc(u)}" target="_blank" rel="noopener">${esc(k)}</a>`).join('')}</div>
      ${m.shot ? `<figure class="shot"><img src="${esc(m.shot.f)}" alt="A screenshot from ${esc(m.name)}" loading="lazy"><figcaption>${m.shot.t ? esc(m.shot.t) + '. ' : ''}From the ${esc(m.name)} gallery on <a href="${esc(m.shot.u)}" target="_blank" rel="noopener">Modrinth</a>.</figcaption></figure>` : ''}
      ${m.long ? `<figure class="authornote"><blockquote><p>${esc(m.long).replace(/\n+/g, '</p><p>')}</p></blockquote><figcaption>From the mod's own description${m.by ? `, by ${esc(m.by)}` : ''}</figcaption></figure>` : ''}
      <dl class="facts"><dt>Category</dt><dd><a href="#/mods?c=${encodeURIComponent(m.cat)}">${esc(m.cat)}</a></dd>${m.by ? `<dt>Made by</dt><dd>${esc(m.by)}</dd>` : ''}<dt>File in the pack</dt><dd>${esc(m.jar)}</dd></dl>
      ${m.m.length ? `<h2 id="mentions">Where this wiki mentions it</h2><ul class="mentions">${m.m.map(x => `<li><a href="#/p/${x.p}${x.a ? '/' + x.a : ''}">${esc(W.pages[x.p].label)}${x.at ? ' · ' + esc(x.at) : ''}</a><p>${esc(x.s)}</p></li>`).join('')}</ul>`
        : `<p class="note">This mod works in the background, so no guide page covers it directly.</p>`}
      ${foot()}</article></div>`;
    return { html, title: m.name, after() {} };
  }
  const notFound = () => ({ html: `<div class="page"><article class="leaf">${banner('start', `<li><a href="#/">Wiki</a></li>`, 'Page not found', slot(groupOf('start').icon))}<p>That page doesn't exist. Use the search at the top, or <a href="#/">go to the home page</a>.</p></article></div>`, title: 'Not found', after() {} });

  /* ---------- the title screen: the menu's own layers, animated and with mouse parallax like in game ---------- */
  let stopHero = () => {};
  function hero() {
    const box = $('.hero'); if (!box || !W.anim) return;
    const S = 3, BW = 341, BH = 190, still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const cv = document.createElement('canvas'); cv.width = BW * S; cv.height = BH * S; cv.className = 'scene'; cv.setAttribute('aria-hidden', 'true');
    const g = cv.getContext('2d'); g.imageSmoothingEnabled = false;
    const load = src => new Promise(ok => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => ok(null); im.src = src; });
    const layers = W.anim.map(l => ({ ...l }));
    let raf = 0, alive = true, onScreen = true, last = 0, mx = 0, my = 0, tx = 0, ty = 0;
    const move = e => { tx = e.clientX / innerWidth - .5; ty = e.clientY / innerHeight - .5; };
    const io = new IntersectionObserver(es => { onScreen = es[0].isIntersecting; if (onScreen && !raf && !still) raf = requestAnimationFrame(draw); });
    function draw(now) {
      raf = 0; if (!alive) return;
      if (now - last >= 33 || still) {
        last = now; mx += (tx - mx) * .12; my += (ty - my) * .12;
        g.clearRect(0, 0, cv.width, cv.height);
        for (const l of layers) {
          if (!l.base) continue;
          let img = l.base;
          if (l.sheet) {
            const k = still ? 0 : Math.floor(now / l.ms) % l.frames;
            if (k !== l.k) { l.k = k; const [x, y, w, h] = l.box; l.g.clearRect(x, y, w, h); l.g.drawImage(l.sheet, (k % l.cols) * w, Math.floor(k / l.cols) * h, w, h, x, y, w, h); }
            img = l.cv;
          }
          g.drawImage(img, Math.round(-mx * l.d * 2 * S), Math.round(-my * l.d * 2 * S), BW * S, BH * S);
        }
      }
      if (!still && onScreen) raf = requestAnimationFrame(draw);
    }
    Promise.all(layers.flatMap(l => [load(`assets/theme/anim/${l.n}.png`).then(im => { l.base = im; }),
      l.box ? load(`assets/theme/anim/${l.n}.sheet.png`).then(im => { l.sheet = im; }) : null])).then(() => {
      if (!alive || !box.isConnected) return;
      layers.forEach(l => { if (l.sheet && l.base) { l.cv = document.createElement('canvas'); l.cv.width = BW; l.cv.height = BH; l.g = l.cv.getContext('2d'); l.g.drawImage(l.base, 0, 0); } else l.sheet = null; });
      box.prepend(cv); draw(performance.now()); requestAnimationFrame(() => box.classList.add('live'));
      if (!still) { addEventListener('pointermove', move, { passive: true }); io.observe(box); }
    });
    stopHero = () => { alive = false; cancelAnimationFrame(raf); removeEventListener('pointermove', move); io.disconnect(); };
  }

  /* ---------- router ---------- */
  function route() {
    const [path, qs] = location.hash.replace(/^#\/?/, '').split('?'); const params = new URLSearchParams(qs || '');
    const parts = path.split('/').filter(Boolean);
    let view, key = '';
    if (!parts.length) { view = home(); key = 'home'; }
    else if (parts[0] === 'p') { view = page(parts[1], parts[2], params); key = 'p/' + parts[1]; }
    else if (parts[0] === 'mods') { view = modsPage(params); key = 'mods'; }
    else if (parts[0] === 'mod') { view = modPage(parts[1]); key = 'mods'; }
    else view = notFound();
    stopHero(); clearInterval(typing);
    const main = $('#main'); main.innerHTML = view.html;
    $$('#side a').forEach(a => a.dataset.r === key ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current'));
    side.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false');
    if (!parts[2]) scrollTo(0, 0);
    view.after();
    document.title = key === 'home' ? 'BSCraft 4 Wiki' : `${view.title} · BSCraft 4 Wiki`;
  }
  addEventListener('hashchange', route);
  route();
})();
