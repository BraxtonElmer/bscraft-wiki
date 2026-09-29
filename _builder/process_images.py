# Downloads the image candidates the research found, converts them to the site format, and records credits.
# Inputs: raw/mods_fetched.json (already downloaded), image_candidates.json (bosses/mobs), image_candidates_mods.json (mods).
import json, os, subprocess, urllib.request, time

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
SITE = os.path.join(HERE, 'site')
UA = {'User-Agent': 'Mozilla/5.0 (bscraft-wiki-builder; raxtray@gmail.com)'}
SKIP_MODS = {'distanthorizons'}   # the guide doesn't showcase graphics mods

credits = json.load(open(os.path.join(HERE, 'image_credits.json'), encoding='utf-8'))
jobs = []   # (kind, slug, raw path, credit)


def fetch(kind, slug, url):
    ext = os.path.splitext(url.split('?')[0])[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.webp', '.gif'):
        ext = '.img'
    dest = os.path.join(RAW, kind, slug + ext)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        ctype = r.headers.get('Content-Type', '')
        data = r.read()
    if not ctype.startswith('image/') and not data[:4] in (b'\x89PNG', b'RIFF', b'GIF8') and data[:2] != b'\xff\xd8':
        raise ValueError('not an image: ' + ctype)
    if len(data) < 2000:
        raise ValueError('too small')
    open(dest, 'wb').write(data)
    return dest


# 1. the Modrinth shots downloaded earlier
done = json.load(open(os.path.join(RAW, 'mods_fetched.json'), encoding='utf-8')) if os.path.exists(os.path.join(RAW, 'mods_fetched.json')) else {}
for slug, v in done.items():
    if slug in SKIP_MODS:
        continue
    jobs.append(('mods', slug, os.path.join(RAW, 'mods', v['raw']), v))

# 2. candidates found by research
failed = []
for fname, kinds in (('image_candidates.json', None), ('image_candidates_mods.json', 'mods')):
    path = os.path.join(HERE, fname)
    if not os.path.exists(path):
        print('not there yet:', fname)
        continue
    data = json.load(open(path, encoding='utf-8'))
    groups = {kinds: data} if kinds else data
    for kind, entries in groups.items():
        for slug, c in entries.items():
            if kind == 'mods' and slug in SKIP_MODS:
                continue
            try:
                dest = fetch(kind, slug, c['url'])
                jobs.append((kind, slug, dest, c))
            except Exception as e:
                failed.append(f'{kind}/{slug}: {type(e).__name__} {str(e)[:60]}')
            time.sleep(0.2)

# 3. convert everything in one PowerShell run
pairs = os.path.join(RAW, 'pairs.txt')
with open(pairs, 'w', encoding='utf-8') as f:
    for kind, slug, src, c in jobs:
        f.write(f'{src}|{os.path.join(SITE, "images", kind, slug + ".jpg")}\n')
out = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                      os.path.join(HERE, 'convert.ps1'), '-Pairs', pairs], capture_output=True, text=True)
print(out.stdout.strip())

# 4. credits for whatever converted
added = 0
for kind, slug, src, c in jobs:
    rel = f'images/{kind}/{slug}.jpg'
    if os.path.exists(os.path.join(SITE, rel)):
        credits.setdefault(kind, {})[slug] = {'file': rel, 'source': c.get('source', ''), 'wiki': c.get('wiki', ''),
                                             'title': c.get('title', '')}
        added += 1
json.dump(credits, open(os.path.join(HERE, 'image_credits.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'credited {added} pictures')
if failed:
    print(f'{len(failed)} downloads failed:')
    for x in failed:
        print('  ', x)
