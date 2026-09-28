# Collect each mod's own metadata (homepage, issue tracker, description, authors) from its jar,
# then match every jar to its Modrinth project by SHA-1 fingerprint. Writes modmeta.json.
import zipfile, glob, os, json, hashlib, tomllib, urllib.request, re
W = os.path.dirname(os.path.abspath(__file__))
MODS = r'C:\Users\raxtr\AppData\Roaming\BSCraft\minecraft\mods'
idx = json.load(open(os.path.join(W, '..', 'modindex.json'), encoding='utf-8'))
byjar = {x['jar']: x['id'] for x in idx}

meta = {}
for jar in glob.glob(os.path.join(MODS, '*.jar')):
    j = os.path.basename(jar)
    if j not in byjar:
        continue
    rec = {'sha1': hashlib.sha1(open(jar, 'rb').read()).hexdigest()}
    try:
        raw = zipfile.ZipFile(jar).read('META-INF/mods.toml').decode('utf-8', 'replace')
        t = tomllib.loads(raw)
        m = (t.get('mods') or [{}])[0]
        for k, src in (('url', 'displayURL'), ('issues', 'issueTrackerURL'), ('desc', 'description'), ('authors', 'authors')):
            v = m.get(src) or t.get(src)
            if isinstance(v, list):
                v = ', '.join(map(str, v))
            if isinstance(v, str) and v.strip() and '${' not in v:
                rec[k] = v.strip()
    except Exception as e:
        rec['err'] = type(e).__name__
    meta[byjar[j]] = rec


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'User-Agent': 'bscraft-wiki-builder/1.0'})
    return json.load(urllib.request.urlopen(req, timeout=60))


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'bscraft-wiki-builder/1.0'})
    return json.load(urllib.request.urlopen(req, timeout=60))


try:
    vf = post('https://api.modrinth.com/v2/version_files', {'hashes': [r['sha1'] for r in meta.values()], 'algorithm': 'sha1'})
    pid_by_sha = {h: v['project_id'] for h, v in vf.items()}
    ids = sorted(set(pid_by_sha.values()))
    projects = {}
    for i in range(0, len(ids), 80):
        chunk = ids[i:i + 80]
        for p in get('https://api.modrinth.com/v2/projects?ids=' + urllib.request.quote(json.dumps(chunk))):
            projects[p['id']] = p
    for mid, r in meta.items():
        pid = pid_by_sha.get(r['sha1'])
        if pid and pid in projects:
            p = projects[pid]
            r['modrinth'] = f"https://modrinth.com/{p.get('project_type', 'mod')}/{p['slug']}"
            r['mr_title'] = p.get('title')
            if p.get('wiki_url'):
                r['mr_wiki'] = p['wiki_url']
            if p.get('source_url'):
                r['source'] = p['source_url']
            if p.get('issues_url') and 'issues' not in r:
                r['issues'] = p['issues_url']
            if p.get('description'):
                r['mr_desc'] = p['description']
except Exception as e:
    print('modrinth lookup failed:', e)

json.dump(meta, open(os.path.join(W, 'modmeta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
c = lambda k: sum(1 for r in meta.values() if k in r)
print(f"{len(meta)} mods | homepage {c('url')} | modrinth {c('modrinth')} | wiki {c('mr_wiki')} | desc {c('desc')} | authors {c('authors')} | errors {c('err')}")
