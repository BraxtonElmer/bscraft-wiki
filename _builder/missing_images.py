# Which picture targets still have no image, per kind. Writes missing_images.json for the fetchers.
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
targets = json.load(open(os.path.join(HERE, 'image_targets.json'), encoding='utf-8'))
credits = json.load(open(os.path.join(HERE, 'image_credits.json'), encoding='utf-8'))
modmeta = json.load(open(os.path.join(HERE, 'modmeta.json'), encoding='utf-8'))
index = json.load(open(os.path.join(HERE, '..', 'modindex.json'), encoding='utf-8'))


def has(kind, slug):
    rec = credits.get(kind, {}).get(slug)
    return bool(rec) and os.path.exists(os.path.join(HERE, 'site', rec['file']))


missing = {}
for kind, items in targets.items():
    rows = []
    for t in items:
        t = dict(t)
        t.setdefault('slug', t.get('id'))   # mod targets are keyed by mod id
        if not has(kind, t['slug']):
            rows.append(t)
    missing[kind] = rows

# mod screenshots: every content mod, including this month's additions, not just the old target list
skip = {'Libraries', 'Performance'}
known = {t['slug'] for t in missing['mods']} | {t.get('id') for t in targets.get('mods', [])}
for m in index:
    if m['cat'] in skip or has('mods', m['id']) or m['id'] in known:
        continue
    missing['mods'].append({'slug': m['id'], 'name': m['name'], 'mod': m['name']})
for t in missing['mods']:
    t['modrinth'] = t.get('modrinth') or modmeta.get(t['slug'], {}).get('modrinth')

json.dump(missing, open(os.path.join(HERE, 'missing_images.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for kind, items in missing.items():
    extra = ''
    if kind == 'mods':
        extra = f" ({sum(1 for t in items if t.get('modrinth'))} have a Modrinth project)"
    print(f'{kind:7s} missing {len(items)}{extra}')
print('sample modrinth field:', next((t['modrinth'] for t in missing['mods'] if t.get('modrinth')), None))
