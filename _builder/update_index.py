# Brings modindex.json in line with the mods folder, matching on the jar file rather than the mod id
# (some jars carry no standard manifest). Keeps existing entries, drops mods that left, adds the new ones.
import json, os, glob, zipfile, tomllib, re

MODS = r'C:/Users/raxtr/AppData/Roaming/BSCraft/minecraft/mods'
HERE = os.path.dirname(os.path.abspath(__file__))
IDX = os.path.join(HERE, 'modindex.json')

NEW = {
    'mca': ('Minecraft Comes Alive Reborn', 'Bosses & Mobs',
            'Villagers become people with names, faces, families and moods. You can befriend them, marry one, raise children, and villages get their own guards.'),
    'fast_travel_waypoints': ('Fast Travel Waypoints', 'Storage, Travel & Utility',
                              "Travel between waystones from Xaero's world map instead of the waystone list. Free, but you have to be standing next to a waystone."),
    'curiouslanterns': ('Curious Lanterns', 'Building & Decoration',
                        'Lanterns you can wear in a Curios slot so they light the way, plus more lantern types to build with.'),
    'fallingtree': ('FallingTree', 'Storage, Travel & Utility',
                    'Breaking one log fells the whole tree, leaves included. Sneak while chopping to turn it off for that tree.'),
    'saplanting': ('Saplanting', 'Storage, Travel & Utility',
                   'Saplings that drop on the ground plant themselves a couple of seconds later, so forests grow back on their own.'),
    'create_enchantment_industry': ('Create: Enchantment Industry', 'Tech & Automation',
                                    'Automates enchanting with Create: liquid experience, printing books, disenchanting, and machines that do it all in a line.'),
    'create_dragons_plus': ('Create: Dragons Plus', 'Libraries',
                            'Shared code for the Dragons Plus Create add-ons, and the dyes and odds and ends they use.'),
}


def stem(j):
    s = re.sub(r'[-_ ]?(forge|fabric|mc|universal)?[-_ ]?v?\d[\w.+]*', '', j[:-4], flags=re.I)
    return re.sub(r'[^a-z0-9]', '', s.lower())


idx = json.load(open(IDX, encoding='utf-8'))
jars = sorted(os.path.basename(p) for p in glob.glob(os.path.join(MODS, '*.jar')))
by_stem = {}
for j in jars:
    by_stem.setdefault(stem(j), j)

out, dropped, rejarred, taken = [], [], [], set()
on_disk = set(jars)
# exact file names first, so two libraries with similar names can't swap places
for e in idx:
    if e['jar'] in on_disk:
        taken.add(e['jar'])
for e in idx:
    j = e['jar'] if e['jar'] in on_disk else None
    if not j:
        cand = by_stem.get(stem(e['jar']))
        j = cand if cand and cand not in taken else None
    if not j:
        dropped.append(e['name'])
        continue
    e = dict(e)
    if e['jar'] != j:
        rejarred.append((e['jar'], j))
        e['jar'] = j
    taken.add(j)
    out.append(e)

# jars with no index entry: the new mods
added = []
for j in jars:
    if j in taken:
        continue
    mid, name = None, j[:-4]
    try:
        z = zipfile.ZipFile(os.path.join(MODS, j))
        t = tomllib.loads(z.read('META-INF/mods.toml').decode('utf-8'))
        m = t.get('mods', [{}])[0]
        mid, name = m.get('modId'), m.get('displayName') or name
    except Exception:
        pass
    if mid in NEW:
        nm, cat, d = NEW[mid]
        out.append({'id': mid, 'name': nm, 'jar': j, 'cat': cat, 'd': d})
        added.append(nm)
    else:
        out.append({'id': mid or name, 'name': name, 'jar': j, 'cat': 'Libraries', 'd': ''})
        added.append('NEEDS DESCRIPTION: ' + str(name))

out.sort(key=lambda m: m['name'].lower())
json.dump(out, open(IDX, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('jars on disk:', len(jars), '| index entries now:', len(out))
print('added:', added)
print('dropped:', dropped)
print('version changes:', rejarred)
print('missing descriptions:', [m['name'] for m in out if not m['d']])
