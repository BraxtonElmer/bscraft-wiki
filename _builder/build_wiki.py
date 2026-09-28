# Build the BSCraft 4 wiki (static site) from the finished guide + mod index + mod jars.
import os, re, json, html, base64, hashlib, shutil, sys, urllib.parse, zipfile
W = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(W)
sys.path.insert(0, W); sys.path.insert(0, SP)
from icons import Resolver, png_size
from modhints import load_index, hint_for
import v2_content as C
from page_guides import GUIDES
MODMETA = json.load(open(os.path.join(W, "modmeta.json"), encoding="utf-8"))

OUT = os.path.join(W, 'site')
_ic = os.path.join(W, 'image_credits.json')
IMG = json.load(open(_ic, encoding='utf-8')) if os.path.exists(_ic) else {}
USED = []


def picture(kind, slug, name):
    rec = IMG.get(kind, {}).get(slug)
    if not rec or not os.path.exists(os.path.join(W, 'site', rec['file'])):
        return ''
    USED.append({'t': rec.get('title') or name, 'u': rec.get('source', ''), 'w': rec.get('wiki', '')})
    return f'<img class="thumb" src="{html.escape(rec["file"])}" alt="{html.escape(name)}" loading="lazy">'
SEP = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
md = open(os.path.join(SP, 'BSCraft-4-Guide.md'), encoding='utf-8').read()
mods = load_index()
R = Resolver()

# ---------------------------------------------------------------- sections
S, order = {}, []
for c in [x.strip() for x in md.split(SEP) if x.strip()]:
    first = c.splitlines()[0]
    if first.startswith('# '):
        t = first[2:].strip(); S[t] = c; order.append(t)
    else:
        S[order[-1]] += '\n\n' + c

GROUPS = [
    ('start', 'Start here', 'daisy', 'What the pack is, what changed from vanilla, the comforts, controls and settings.'),
    ('explore', 'Explore', 'cornflower', 'Biomes, structures, the Nether and End, the Twilight Forest, Alex\'s Caves, space and ores.'),
    ('fight', 'Fight', 'poppy', 'Bosses, weapons, armor, enchantments, powers and how to get the good gear.'),
    ('magic', 'Magic', 'allium', 'Two spell systems, one mana bar, and every addon that grows them.'),
    ('creatures', 'Creatures', 'petals', 'Mobs, tames, mounts and the full bestiary.'),
    ('tech', 'Tech', 'torchflower', 'Create, power, RFTools, reactors and the bigger machines.'),
    ('everyday', 'Everyday', 'lily', 'Food, drinks, building and handy gadgets.'),
    ('reference', 'Reference', 'sunflower', 'Every mod in the pack, and where to read more.'),
]
PAGES = [  # title, group, slug, short label
    ('What BSCraft 4 is', 'start', 'what-is-bscraft', 'What BSCraft 4 is'),
    ("What's different from vanilla", 'start', 'vs-vanilla', 'Different from vanilla'),
    ('Quality of life', 'start', 'quality-of-life', 'Quality of life'),
    ('Controls and info tools', 'start', 'controls', 'Controls'),
    ('Settings worth changing', 'start', 'settings', 'Settings'),
    ('What you can do in BSCraft', 'start', 'what-you-can-do', 'What you can do'),
    ('Difficulty tiers', 'start', 'difficulty', 'Difficulty tiers'),
    ('Ways people play', 'start', 'ways-to-play', 'Ways people play'),
    ('Biomes', 'explore', 'biomes', 'Biomes'),
    ('Structures and best loot', 'explore', 'structures', 'Structures & loot'),
    ('The Nether and the End', 'explore', 'nether-end', 'Nether & End'),
    ('The Twilight Forest', 'explore', 'twilight-forest', 'Twilight Forest'),
    ("Alex's Caves", 'explore', 'alexs-caves', "Alex's Caves"),
    ('Space, ships and aircraft', 'explore', 'space-and-vehicles', 'Space & vehicles'),
    ('Ores and resources', 'explore', 'ores', 'Ores'),
    ('Bosses', 'fight', 'bosses', 'Bosses'),
    ('Weapons compared', 'fight', 'weapons', 'Weapons'),
    ('Ranged weapons and gadgets', 'fight', 'ranged', 'Ranged & gadgets'),
    ('Armor compared', 'fight', 'armor', 'Armor'),
    ('Enchantments', 'fight', 'enchantments', 'Enchantments'),
    ('Powers and accessories', 'fight', 'powers', 'Powers & accessories'),
    ('How to get every weapon and armor', 'fight', 'getting-gear', 'Getting gear'),
    ('Magic', 'magic', 'magic', 'How magic works'),
    ('Ars Nouveau', 'magic', 'ars-nouveau', 'Ars Nouveau'),
    ("Iron's Spells 'n Spellbooks", 'magic', 'irons-spells', "Iron's Spells"),
    ('Creatures', 'creatures', 'creatures', 'Creatures'),
    ('Villagers and families', 'creatures', 'villagers', 'Villagers'),
    ('Mounts and companions', 'creatures', 'mounts', 'Mounts & companions'),
    ('Bestiary', 'creatures', 'bestiary', 'Bestiary'),
    ('Create and power', 'tech', 'create', 'Create & power'),
    ('RFTools and Bigger Reactors', 'tech', 'rftools', 'RFTools & reactors'),
    ('How the bigger systems work', 'tech', 'systems', 'Bigger systems'),
    ('Food and drink', 'everyday', 'food', 'Food & drink'),
    ('Building and gadgets', 'everyday', 'building', 'Building & gadgets'),
    ('Where to read more', 'reference', 'read-more', 'Where to read more'),
]
SLUG = {t: s for t, g, s, l in PAGES}

# ---------------------------------------------------------------- icons
ICONS = {}   # key -> data uri


def icon_for(name, paren=None, suffixes=('',)):
    first = re.split(r' / | or ', re.sub(r'\s*\(.*?\)', '', name))[0].strip()
    h = hint_for(paren) if paren else None
    for suf in suffixes:
        r = R.find(first + suf, h)
        if r:
            data = r[0]
            if len(data) > 40000:
                return None
            key = hashlib.md5(data).hexdigest()[:10]
            if key not in ICONS:
                w, hgt = png_size(data)
                ICONS[key] = ('data:image/png;base64,' + base64.b64encode(data).decode(), hgt > w)
            return key
    return None


# ---------------------------------------------------------------- mod links in text
NO_AUTOLINK = {'create', 'spawn', 'sit', 'jade', 'comforts', 'artifacts', 'waystones', 'corpse', 'polymorph', 'athena', 'fusion',
               'particular', 'balm', 'platform', 'wheel', 'prism', 'quartz', 'saturn', 'curios api', 'melody', 'konkrete', 'citadel',
               'botarium', 'bookshelf', 'iceberg', 'lightspeed', 'starlight', 'krypton reforged', 'jei'}
link_names = {}
for x in mods:
    if x['cat'] == 'Libraries':
        continue
    n = x['name']
    if n.lower() in NO_AUTOLINK or len(n) < 5:
        continue
    link_names[n] = x['id']
EXTRA = {"Iron's Spells": 'irons_spellbooks', 'Magic From The East': 'iss_magicfromtheeast', 'BetterEnd': 'betterend', 'BetterNether': 'betternether',
         'Alex\'s Caves': 'alexscaves', 'Twilight Forest': 'twilightforest', "Mowzie's Mobs": 'mowziesmobs', 'Simply Swords': 'simplyswords',
         "Bosses'Rise": 'block_factorys_bosses', 'Immersive Armors': 'immersive_armors', 'Armor of the Ages': 'armoroftheages',
         'Dark Doppelganger': 'darkdoppelganger', "Adam's Ars Plus": 'adamsarsplus', 'Ars Elemental': 'ars_elemental', 'Ars Nouveau': 'ars_nouveau',
         "Ars 'n Spells": 'ars_n_spells', 'Geomancy Plus': 'gtbcs_geomancy_plus', "Farmer's Delight": 'farmersdelight', 'Valkyrien Skies': 'valkyrienskies',
         'Sophisticated Backpacks': 'sophisticatedbackpacks', 'Lootr': 'lootr', 'Northstar': 'northstar', 'Aquamirae': 'aquamirae',
         'The Graveyard': 'graveyard', 'Bygone Nether': 'bygonenether', 'RFTools': 'rftoolsutility', 'Bigger Reactors': 'biggerreactors'}
ids = {x['id'] for x in mods}
for k, v in EXTRA.items():
    if v in ids:
        link_names[k] = v
LINK_RX = re.compile(r'(?<![\w\'])(' + '|'.join(re.escape(html.escape(n, quote=False)) for n in sorted(link_names, key=len, reverse=True)) + r')(?![\w])')
ESC2ID = {html.escape(k, quote=False): v for k, v in link_names.items()}

KEYLIKE = re.compile(r'^[A-Za-z0-9 +/]{1,24}$')


def inline(s, linked=None):
    s = html.escape(s, quote=False)
    urls = []
    def keep_url(m):
        urls.append(m.group(1)); return f'\x00{len(urls) - 1}\x00'
    s = re.sub(r'&lt;(https?://[^\s&]+(?:&amp;[^\s&]+)*)&gt;', keep_url, s)
    codes = []
    def keep_code(m):
        t = m.group(1)
        if KEYLIKE.match(t) and '.' not in t:
            parts = [p.strip() for p in t.split('+')] if '+' in t else [t]
            out = '<span class="keys">' + '<span class="plus">+</span>'.join(f'<kbd>{p}</kbd>' for p in parts) + '</span>'
        else:
            out = f'<code>{t}</code>'
        codes.append(out); return f'\x01{len(codes) - 1}\x01'
    s = re.sub(r'`([^`]+)`', keep_code, s)
    if linked is not None:
        def lk(m):
            mid = ESC2ID.get(m.group(1))
            if not mid or mid in linked:
                return m.group(1)
            linked.add(mid)
            return f'<a class="modlink" href="#/mod/{mid}">{m.group(1)}</a>'
        s = LINK_RX.sub(lk, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\x01(\d+)\x01', lambda m: codes[int(m.group(1))], s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: f'<a href="{urls[int(m.group(1))]}" target="_blank" rel="noopener">{urls[int(m.group(1))].split("//")[1].rstrip("/")}</a>', s)
    return s.strip()


def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:60] or 'x'


TABLES = {
    'Weapons compared': (['Weapon', 'From', 'Dmg', 'Speed', 'DPS', 'Durability', 'Notes', 'Tier'],
                         [r'((?:about )?[\d.]+(?: or [\d.]+)?)\s+damage', r'([\d.]+(?: or [\d.]+)?)\s+speed', r'((?:about )?[\d.]+)\s+DPS', r'([\d,]+|unbreakable|netherite)\s+durability'], (' Sword', '')),
    'Armor compared': (['Set', 'From', 'Armor', 'Tough.', 'KB res', 'Chest dur.', 'Notes', 'Tier'],
                       [r'([\d.]+)\s+armor', r'([\d.]+)\s+toughness', r'([\d.]+)\s+KB res', r'((?:about )?[\d,]+(?: or [\d,]+)?)\s+chest durability'], (' Chestplate', ' Robes', ' Robe', ' Chestplate Armor', '')),
    'Bosses': (['Boss', 'From', 'HP', 'Armor', 'Damage', 'Notes', 'Tier'],
               [r'((?:about )?[\d,]+(?: (?:plus|to) [\d,]+)?)\s+HP', r'([\d.]+)\s+armor', r'([\d.]+(?: to [\d.]+)?(?: and [\d.]+)?)\s+damage'], None),
}
NUMCOLS = {'Dmg', 'Speed', 'DPS', 'Durability', 'Armor', 'Tough.', 'KB res', 'Chest dur.', 'HP', 'Damage'}
BOSS_CARDS = []


def first(rx, s, default='-'):
    m = re.search(rx, s)
    return m.group(1) if m else default


def table_row(title, item, linked):
    cols, rxs, sufs = TABLES[title]
    m = re.match(r'\*\*(.+?)\*\*(.*?)\s*\(([^()]*)\)\s*:\s*(.*)$', item)
    if not m:
        return None
    name, extra, mod, rest = m.group(1), m.group(2), m.group(3), m.group(4)
    tier = first(r'Tier ([SABC])(?: for casters)?\.?\s*$', rest, '')
    rest = re.sub(r'\s*Tier [SABC](?: for casters)?\.?\s*$', '', rest)
    stats, _, notes = rest.partition('. ')
    vals = [first(rx, stats) for rx in rxs]
    if title == 'Bosses':
        notes = rest.partition('. ')[2] if 'HP' in stats else rest
        BOSS_CARDS.append({'name': name, 'mod': mod, 'hp': vals[0], 'tier': tier, 'slug': slugify(name)})
        lead = picture('bosses', slugify(name), name)
    else:
        key = icon_for(name, mod, sufs)
        lead = f'<span class="icon"><i class="ico i-{key}"></i></span>' if key else '<span class="icon" aria-hidden="true"></span>'
    cells = [f'<th scope="row"><div class="nc">{lead}<span class="nm">{inline(name + extra)}</span></div></th>', f'<td class="from">{inline(mod, linked)}</td>']
    cells += [f'<td class="n">{html.escape(v)}</td>' for v in vals]
    cells += [f'<td class="notes">{inline(notes)}</td>', '<td>' + (f'<span class="tier t{tier}" title="Tier {tier}">{tier}</span>' if tier else '') + '</td>']
    return '<tr>' + ''.join(cells) + '</tr>'


ENTRY_RX = re.compile(r'^\*\*(.+?)\*\*([^:(]*?)(?:\s*\(([^()]*)\))?\s*:\s+(.+)$')


def convert(title, text):
    lines = text.splitlines()
    o, toc, linked = [], [], set()
    state = {'list': None, 'buf': [], 'quote': [], 'tabled': False}
    used_ids = set()

    def hid(t):
        b = slugify(t); i = b; n = 2
        while i in used_ids:
            i = f'{b}-{n}'; n += 1
        used_ids.add(i); return i

    def entry_html(x):
        m = ENTRY_RX.match(x)
        name, extra, src, rest = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
        key = icon_for(name, src)
        icon = f'<span class="icon"><i class="ico i-{key}"></i></span>' if key else ''
        first_name = re.split(r' / |, | and ', re.sub(r'\s*\(.*?\)', '', name))[0].strip()
        pic = picture('mobs', slugify(first_name), first_name) or picture('bosses', slugify(first_name), first_name)
        if pic:
            icon = pic
        srch = f'<span class="src">{inline(src, linked)}</span>' if src else ''
        return (f'<div class="entry{"" if icon else " noicon"}">{icon}<dt><span class="nm">{inline(name + (" " + extra if extra else ""))}</span>{srch}</dt>'
                f'<dd>{inline(rest, linked)}</dd></div>')

    def flush_list():
        if not state['list']:
            return
        buf = state['buf']
        if title in TABLES and not state['tabled'] and state['list'] == 'ul':
            rows = [table_row(title, x, linked) for x in buf]
            if rows and all(rows):
                cols = TABLES[title][0]
                ths = ''.join(f'<th scope="col" class="n">{c}</th>' if c in NUMCOLS else f'<th scope="col">{c}</th>' for c in cols)
                fid = 'filter-' + slugify(title)
                o.append(f'<div class="tabletools"><label for="{fid}">Filter</label><input id="{fid}" type="search" placeholder="Name, mod or tier"><output for="{fid}"></output></div>')
                o.append(f'<div class="tablewrap"><table class="db"><thead><tr>{ths}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
                state.update(list=None, buf=[], tabled=True)
                return
        if state['list'] == 'ul':
            # runs of "Name (source): details" become a definition list, the rest stay bullets
            runs, cur, kind = [], [], None
            for x in buf:
                k = bool(ENTRY_RX.match(x))
                if cur and k != kind:
                    runs.append((kind, cur)); cur = []
                cur.append(x); kind = k
            if cur:
                runs.append((kind, cur))
            for k, items in runs:
                if k:
                    o.append('<dl class="entries">' + ''.join(entry_html(x) for x in items) + '</dl>')
                else:
                    o.append('<ul>' + ''.join(f'<li>{inline(x, linked)}</li>' for x in items) + '</ul>')
        else:
            o.append('<ol>' + ''.join(f'<li>{inline(x, linked)}</li>' for x in buf) + '</ol>')
        state.update(list=None, buf=[])

    def flush_quote():
        if state['quote']:
            o.append('<aside class="note">' + ''.join(f'<p>{inline(q, linked)}</p>' for q in state['quote']) + '</aside>')
            state['quote'] = []

    for ln in lines:
        if ln.strip() == SEP or ln.startswith('# '):
            continue
        if ln.startswith('> '):
            flush_list(); state['quote'].append(ln[2:]); continue
        flush_quote()
        if ln.startswith('## '):
            flush_list(); t = ln[3:].strip(); i = hid(t); toc.append({'id': i, 't': re.sub(r'\*\*', '', t)})
            o.append(f'<h2 id="{i}">{inline(t)}</h2>'); continue
        if ln.startswith('### '):
            flush_list(); t = ln[4:].strip(); i = hid(t)
            o.append(f'<h3 id="{i}">{inline(t)}</h3>'); continue
        if ln.startswith('-# '):
            flush_list(); o.append(f'<p class="fine">{inline(ln[3:], linked)}</p>'); continue
        m = re.match(r'- (.*)', ln)
        if m:
            if state['list'] != 'ul': flush_list(); state['list'] = 'ul'
            state['buf'].append(m.group(1)); continue
        m = re.match(r'\d+\. (.*)', ln)
        if m:
            if state['list'] != 'ol': flush_list(); state['list'] = 'ol'
            state['buf'].append(m.group(1)); continue
        flush_list()
        if ln.strip():
            o.append(f'<p>{inline(ln, linked)}</p>')
    flush_list(); flush_quote()
    return '\n'.join(o), toc


pages = {}
for title, grp, slug, label in PAGES:
    USED.clear()
    body, toc = convert(title, S[title])
    credits = [dict(t) for t in {tuple(sorted(c.items())) for c in USED}]
    txt = re.sub(r'<[^>]+>', '', body)
    lede = re.sub(r'\s+', ' ', txt).strip()[:180]
    pages[slug] = {'title': title, 'label': label, 'group': grp, 'html': body, 'toc': toc, 'lede': lede, 'credits': sorted(credits, key=lambda c: c['t'])}

# ---------------------------------------------------------------- mods: mentions, wiki links
wiki_links = {}
for ln in C.READ_MORE.splitlines():
    m = re.match(r'- (.+?): <(https?://[^>]+)>', ln)
    if m:
        wiki_links[m.group(1).strip()] = m.group(2)
WIKI_ID = {'Ars Nouveau': 'ars_nouveau', "Iron's Spells 'n Spellbooks": 'irons_spellbooks', "Ars 'n Spells": 'ars_n_spells', "Alex's Caves": 'alexscaves',
           "Alex's Mobs": 'alexsmobs', "Mowzie's Mobs": 'mowziesmobs', 'Twilight Forest': 'twilightforest', 'BetterEnd': 'betterend',
           'Simply Swords': 'simplyswords', 'Artifacts': 'artifacts', 'Ensorcellation': 'ensorcellation', 'Create': 'create',
           'Valkyrien Skies 2': 'valkyrienskies', 'RFTools': 'rftoolsutility', 'CC: Tweaked': 'computercraft', "Farmer's Delight": 'farmersdelight',
           "Brewin' and Chewin'": 'brewinandchewin', 'Croptopia': 'croptopia', 'Supplementaries': 'supplementaries', 'Waystones': 'waystones'}
mod_wiki = {WIKI_ID[k]: v for k, v in wiki_links.items() if k in WIKI_ID}

name_variants = {}
for x in mods:
    vs = {x['name']}
    for k, v in EXTRA.items():
        if v == x['id']:
            vs.add(k)
    name_variants[x['id']] = [v for v in vs if len(v) >= 4]

logo_dir = os.path.join(W, 'logos')
mod_out = []
for x in mods:
    mentions = []
    if x['cat'] != 'Libraries':
        rx = re.compile(r'(?<![\w])(' + '|'.join(re.escape(v) for v in name_variants[x['id']]) + r')(?![\w])')
        for title, grp, slug, label in PAGES:
            anchor, anchor_t = '', ''
            for ln in S[title].splitlines():
                if ln.startswith('## '):
                    anchor_t = ln[3:].strip(); anchor = slugify(anchor_t)
                if ln.startswith('#') or not rx.search(ln):
                    continue
                snip = re.sub(r'\*\*|`|<|>', '', re.sub(r'^[-\d.>#\s]+', '', ln)).strip()
                if len(snip) > 220:
                    snip = snip[:217].rsplit(' ', 1)[0] + '…'
                mentions.append({'p': slug, 'a': anchor, 'at': anchor_t, 's': snip})
                if len(mentions) >= 10:
                    break
            if len(mentions) >= 10:
                break
    mm = MODMETA.get(x['id'], {})
    links = []
    wiki = mod_wiki.get(x['id']) or mm.get('mr_wiki')
    if mm.get('modrinth'):
        links.append(['Modrinth', mm['modrinth']])
    home = mm.get('url')
    if home and home.startswith('http') and 'modrinth.com' not in home:
        links.append(['CurseForge' if 'curseforge.com' in home else 'Homepage', home])
    if not links:
        links.append(['Search on CurseForge', 'https://www.curseforge.com/minecraft/search?search=' + urllib.parse.quote(x['name'])])
    if mm.get('source') and mm['source'] != home:
        links.append(['Source code', mm['source']])
    if mm.get('issues') and mm['issues'].startswith('http'):
        links.append(['Report a bug', mm['issues']])
    long = (mm.get('desc') or '').strip()
    if mm.get('mr_desc') and len(mm['mr_desc']) > len(long):
        long = mm['mr_desc'].strip()
    long = re.sub(r'\s+\n', '\n', long).strip()
    if len(long) > 900:
        long = long[:897].rsplit(' ', 1)[0] + '…'
    mod_out.append({'id': x['id'], 'name': x['name'], 'cat': x['cat'], 'd': x['d'], 'jar': x['jar'],
                    'logo': os.path.exists(os.path.join(logo_dir, x['id'] + '.png')), 'wiki': wiki, 'm': mentions,
                    'links': links, 'by': mm.get('authors', ''), 'shot': ({'f': IMG['mods'][x['id']]['file'], 'u': IMG['mods'][x['id']].get('source', ''), 't': IMG['mods'][x['id']].get('title', '')} if x['id'] in IMG.get('mods', {}) and os.path.exists(os.path.join(W, 'site', IMG['mods'][x['id']]['file'])) else None), 'long': long if long.lower().rstrip('.') != x['d'].lower().rstrip('.') else ''})

# page explanations and further reading
MOD_BY_ID = {m['id']: m for m in mod_out}
for title, grp, slug, label in PAGES:
    gd = GUIDES.get(slug, {})
    pages[slug]['about'] = gd.get('about', [])
    pages[slug]['how'] = gd.get('how', '')
    reads = []
    for mid in gd.get('mods', []):
        m = MOD_BY_ID.get(mid)
        if not m:
            continue
        if m['wiki']:
            reads.append({'id': mid, 'name': m['name'], 'u': m['wiki'], 'k': 'Official wiki'})
        else:
            reads.append({'id': mid, 'name': m['name'], 'u': m['links'][0][1], 'k': m['links'][0][0]})
    pages[slug]['read'] = reads

# let slash-joined names ("Bluejay/Cardinal/Canary/Robin") wrap on phones: a break opportunity after each slash in text (never inside tags)
def soft_slash(h):
    return ''.join(part if part.startswith('<') else re.sub(r'/(?=\w)', '/<wbr>', part) for part in re.split(r'(<[^>]+>)', h))
for slug in pages:
    pages[slug]['html'] = soft_slash(pages[slug]['html'])

# ---------------------------------------------------------------- search index
search = []
for slug, p in pages.items():
    search.append({'t': p['label'], 'k': 'Page', 'u': f'#/p/{slug}', 's': p['lede'][:120]})
    for h in p['toc']:
        search.append({'t': h['t'], 'k': p['label'], 'u': f'#/p/{slug}/{h["id"]}', 's': ''})
    for m in re.finditer(r'<(?:li|tr)>(.*?)</(?:li|tr)>|<div class="entry[^"]*">(.*?)</div>', p['html']):
        inner = m.group(1) or m.group(2)
        nm = re.search(r'class="nm">(.+?)</span>', inner) or re.search(r'<strong>(.+?)</strong>', inner)
        if not nm:
            continue
        name = re.sub(r'<[^>]+>', '', nm.group(1))
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', inner)).strip()
        search.append({'t': name, 'k': p['label'], 'u': f'#/p/{slug}', 's': text[:140], 'q': name})
for mo in mod_out:
    search.append({'t': mo['name'], 'k': 'Mod', 'u': f'#/mod/{mo["id"]}', 's': mo['d'][:120]})

# ---------------------------------------------------------------- home data
bis_html = soft_slash(convert('bis', S['What BSCraft 4 is'].split('## Best in slot, at a glance', 1)[1])[0])
qol_html = soft_slash(convert('qol', S['What BSCraft 4 is'].split('## The quality-of-life stuff that matters most', 1)[1].split('## Best in slot', 1)[0])[0])
intro = next(pp.strip() for pp in S['BSCraft 4 guide'].split('\n\n') if pp.startswith('This is a guide'))

# ---------------------------------------------------------------- menu icons: one item per group and page
# "mc:" names are vanilla textures read from the pack's own 1.20.1 jar; the rest resolve through the mod jars.
VANILLA_JAR = os.path.join(os.environ['APPDATA'], 'BSCraft', 'minecraft', 'versions', '1.20.1', '1.20.1.jar')
_vz = zipfile.ZipFile(VANILLA_JAR) if os.path.exists(VANILLA_JAR) else None
def nav_icon(name):
    if name.startswith('mc:'):
        if not _vz:
            return None
        for folder in ('item', 'block'):
            try:
                raw = _vz.read(f'assets/minecraft/textures/{folder}/{name[3:]}.png')
            except KeyError:
                continue
            key = hashlib.md5(raw).hexdigest()[:10]
            if key not in ICONS:
                w, hgt = png_size(raw)
                ICONS[key] = ('data:image/png;base64,' + base64.b64encode(raw).decode(), hgt > w)
            return key
        return None
    return icon_for(name)
GROUP_ICON = {'start': 'mc:compass_19', 'explore': 'mc:filled_map', 'fight': 'mc:diamond_sword', 'magic': 'Arcane Essence',
              'creatures': 'mc:egg', 'tech': 'Cogwheel', 'everyday': 'mc:bread', 'reference': 'mc:book'}
PAGE_ICON = {'what-is-bscraft': 'mc:written_book', 'vs-vanilla': 'mc:knowledge_book', 'quality-of-life': 'mc:bundle', 'controls': 'mc:spyglass',
             'settings': 'mc:comparator', 'what-you-can-do': 'mc:iron_pickaxe', 'difficulty': 'mc:totem_of_undying', 'ways-to-play': 'mc:campfire',
             'biomes': 'mc:oak_sapling', 'structures': 'mc:filled_map', 'nether-end': 'mc:ender_eye', 'twilight-forest': 'Glass Sword',
             'alexs-caves': 'mc:amethyst_shard', 'space-and-vehicles': 'mc:firework_rocket', 'ores': 'mc:diamond', 'bosses': 'mc:nether_star',
             'weapons': 'mc:netherite_sword', 'ranged': 'mc:bow', 'armor': 'mc:diamond_chestplate', 'enchantments': 'mc:enchanted_book',
             'powers': 'mc:heart_of_the_sea', 'getting-gear': 'mc:experience_bottle', 'magic': 'Arcane Essence', 'ars-nouveau': 'Source Gem',
             'irons-spells': 'Spell Book', 'creatures': 'mc:bone', 'villagers': 'mc:emerald', 'mounts': 'mc:saddle', 'bestiary': 'mc:writable_book', 'create': 'Cogwheel',
             'rftools': 'mc:redstone', 'systems': 'mc:clock_00', 'food': 'mc:cake', 'building': 'mc:brick', 'read-more': 'mc:book'}
for slug in pages:
    pages[slug]['icon'] = nav_icon(PAGE_ICON.get(slug, '')) if PAGE_ICON.get(slug) else None
missing = [s for s in pages if not pages[s]['icon']]
if missing:
    print('no nav icon for', missing)
ANIM = json.load(open(os.path.join(W, 'theme', 'anim.json'), encoding='utf-8-sig'))   # made by make_anim.ps1

data = {'meta': {'mods': len(mods), 'mc': '1.20.1', 'forge': '47.4.10'},
        'groups': [{'id': g, 'name': n, 'icon': nav_icon(GROUP_ICON[g]), 'blurb': b, 'pages': [s for t, gg, s, l in PAGES if gg == g]} for g, n, f, b in GROUPS],
        'pages': pages, 'mods': mod_out, 'cats': C.CAT_ORDER, 'search': search, 'bis': bis_html, 'qol': qol_html,
        'bosses': BOSS_CARDS, 'intro': intro, 'anim': ANIM}

# ---------------------------------------------------------------- write
if os.path.exists(OUT):
    for sub in ('assets',):
        shutil.rmtree(os.path.join(OUT, sub), ignore_errors=True)
os.makedirs(os.path.join(OUT, 'assets', 'logos'), exist_ok=True)
for d in ('images/bosses', 'images/mobs', 'images/places'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
open(os.path.join(OUT, 'assets', 'data.js'), 'w', encoding='utf-8').write('window.WIKI=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';')
css = []
for k, (uri, anim) in ICONS.items():
    css.append(f'.i-{k}{{background-image:url({uri})' + (';background-size:100% auto;background-position:top' if anim else '') + '}')
open(os.path.join(OUT, 'assets', 'icons.css'), 'w', encoding='utf-8').write('\n'.join(css))
for f in os.listdir(logo_dir):
    shutil.copy(os.path.join(logo_dir, f), os.path.join(OUT, 'assets', 'logos', f))
shutil.copy(os.path.join(W, 'src', 'app.js'), os.path.join(OUT, 'assets', 'app.js'))
shutil.copytree(os.path.join(W, 'theme'), os.path.join(OUT, 'assets', 'theme'))   # art from the pack's main menu (make_theme.ps1)
with open(os.path.join(OUT, 'assets', 'style.css'), 'w', encoding='utf-8') as f:   # the forest menu theme
    for part in ('forest.css',):
        f.write(open(os.path.join(W, 'src', part), encoding='utf-8').read() + chr(10))
frag = open(os.path.join(W, 'src', 'index.html'), encoding='utf-8').read()
for asset in ('style.css', 'icons.css', 'data.js', 'app.js'):   # cache-busting stamps so visitors always get the current build
    ver = hashlib.md5(open(os.path.join(OUT, 'assets', asset), 'rb').read()).hexdigest()[:8]
    frag = frag.replace(f'assets/{asset}"', f'assets/{asset}?v={ver}"')
open(os.path.join(W, 'preview.html'), 'w', encoding='utf-8').write(frag)   # the Artifact preview wraps this itself
head, _, bodyhtml = frag.partition('<a class="skip"')
full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<link rel="icon" href="assets/theme/portrait.png">\n' + head.strip() + '\n</head>\n<body>\n<a class="skip"'
        + bodyhtml.strip() + '\n</body>\n</html>\n')
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(full)
readme = '''BSCraft 4 Wiki - static site

Open index.html in a browser, or upload this whole folder to any static host
(GitHub Pages, Cloudflare Pages, Netlify, or your own web server). No server code needed.

Pictures you can add later (PNG, any size, square looks best):
  images/bosses/<boss-name>.png   e.g. images/bosses/dark-doppelganger.png
  The site shows them automatically; missing ones fall back to a letter badge.
  Boss file names: ''' + ', '.join(b['slug'] for b in BOSS_CARDS) + '''

Rebuild from the guide with build_wiki.py (see the scratchpad project).
'''
open(os.path.join(OUT, 'README.txt'), 'w', encoding='utf-8').write(readme)
print(f'pages {len(pages)}, mods {len(mod_out)}, icons {len(ICONS)}, search {len(search)}, bosses {len(BOSS_CARDS)}')
print('data.js KB', os.path.getsize(os.path.join(OUT, 'assets', 'data.js')) // 1024, 'icons.css KB', os.path.getsize(os.path.join(OUT, 'assets', 'icons.css')) // 1024)
