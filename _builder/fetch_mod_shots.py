# Pulls one gallery picture per mod from Modrinth for mods whose page has no screenshot yet.
# Picks the featured image, else the first. Saves the original to raw/, then resize.ps1 makes the site copy.
import json, os, re, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw', 'mods')
os.makedirs(RAW, exist_ok=True)
missing = json.load(open(os.path.join(HERE, 'missing_images.json'), encoding='utf-8'))['mods']
UA = {'User-Agent': 'bscraft-wiki-builder/1.0 (raxtray@gmail.com)'}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))


got, none, failed = {}, [], []
for t in missing:
    link = t.get('modrinth')
    if not link:
        continue
    slug = link.rstrip('/').split('/')[-1]
    try:
        p = get_json(f'https://api.modrinth.com/v2/project/{slug}')
    except Exception as e:
        failed.append((t['slug'], type(e).__name__))
        continue
    gal = p.get('gallery') or []
    if not gal:
        none.append(t['name'])
        continue
    pick = next((g for g in gal if g.get('featured')), None) or sorted(gal, key=lambda g: g.get('ordering', 0))[0]
    url = pick['url']
    ext = os.path.splitext(url.split('?')[0])[1].lower() or '.png'
    dest = os.path.join(RAW, t['slug'] + ext)
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=60).read()
        open(dest, 'wb').write(data)
    except Exception as e:
        failed.append((t['slug'], 'download ' + type(e).__name__))
        continue
    got[t['slug']] = {'raw': os.path.basename(dest), 'source': link, 'wiki': 'Modrinth',
                      'title': (pick.get('title') or p.get('title') or t['name']).strip()}
    time.sleep(0.25)   # be polite to the API

json.dump(got, open(os.path.join(HERE, 'raw', 'mods_fetched.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
size = sum(os.path.getsize(os.path.join(RAW, v['raw'])) for v in got.values())
print(f'downloaded {len(got)} screenshots, {size / 1048576:.1f} MB raw')
print('no gallery on Modrinth:', len(none), '-', ', '.join(none[:20]))
print('failed:', failed[:10])
