# Resolve item names (as written in the guide) to their in-game texture PNG bytes, straight from the mod jars.
import zipfile, glob, json, re, os, struct
MODS = r'C:\Users\raxtr\AppData\Roaming\BSCraft\minecraft\mods'
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lang_index.json')


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


class Resolver:
    def __init__(self):
        self.jars = {}          # namespace -> list of jar paths that contain assets/<ns>/
        self.names = {}         # normalized display name -> list of (ns, kind, path)
        self._zips = {}
        self._build()

    def _zip(self, p):
        if p not in self._zips:
            self._zips[p] = zipfile.ZipFile(p)
        return self._zips[p]

    def _build(self):
        if os.path.exists(CACHE):
            d = json.load(open(CACHE, encoding='utf-8'))
            self.jars, self.names = d['jars'], d['names']
            return
        for jar in glob.glob(os.path.join(MODS, '*.jar')):
            try:
                z = zipfile.ZipFile(jar)
            except Exception:
                continue
            nss = set()
            for n in z.namelist():
                m = re.match(r'assets/([^/]+)/', n)
                if m:
                    nss.add(m.group(1))
                if n.endswith('lang/en_us.json'):
                    try:
                        lang = json.loads(z.read(n).decode('utf-8', 'replace'))
                    except Exception:
                        continue
                    for k, v in lang.items():
                        mm = re.match(r'^(item|block)\.([a-z0-9_.-]+)\.([a-z0-9_/.-]+)$', k)
                        if mm and isinstance(v, str) and '%' not in v:
                            self.names.setdefault(norm(v), []).append((mm.group(2), mm.group(1), mm.group(3)))
            for ns in nss:
                self.jars.setdefault(ns, []).append(jar)
        json.dump({'jars': self.jars, 'names': self.names}, open(CACHE, 'w', encoding='utf-8'))

    def _read(self, ns, path):
        for jar in self.jars.get(ns, []):
            z = self._zip(jar)
            try:
                return z.read(path)
            except KeyError:
                continue
        return None

    def _model_texture(self, ns, kind, path, depth=0):
        """Follow an item model to its first texture layer."""
        if depth > 4:
            return None
        raw = self._read(ns, f'assets/{ns}/models/{kind}/{path}.json')
        if not raw:
            return None
        try:
            mdl = json.loads(raw.decode('utf-8', 'replace'))
        except Exception:
            return None
        tex = mdl.get('textures', {})
        for key in ('layer0', 'all', 'side', 'top', 'texture', 'particle', 'front', 'end', 'cross', 'plant'):
            if key in tex and not str(tex[key]).startswith('#'):
                return tex[key]
        parent = mdl.get('parent', '')
        if parent and not parent.startswith(('minecraft:item/generated', 'item/generated', 'minecraft:item/handheld', 'builtin')):
            pns, _, ppath = parent.partition(':') if ':' in parent else (ns, None, parent)
            pk, _, pp = ppath.partition('/')
            return self._model_texture(pns, pk, pp, depth + 1)
        return None

    def texture(self, ns, kind, path):
        cands = []
        t = self._model_texture(ns, 'item', path)
        if t:
            cands.append(t)
        cands += [f'{ns}:item/{path}', f'{ns}:block/{path}']
        for c in cands:
            tns, _, tp = c.partition(':') if ':' in c else ('minecraft', None, c)
            data = self._read(tns, f'assets/{tns}/textures/{tp}.png')
            if data and data[:8] == b'\x89PNG\r\n\x1a\n':
                return data
        return None

    def find(self, name, mod_hint=None):
        """Return (png_bytes, ns) for a display name, preferring the hinted mod namespace(s)."""
        opts = self.names.get(norm(name), [])
        if not opts:
            return None
        if mod_hint:
            hinted = [o for o in opts if o[0] in mod_hint]
            if hinted:
                opts = hinted + [o for o in opts if o not in hinted]
            elif len({o[0] for o in opts}) > 1:
                return None  # ambiguous and none from the named mod
        for ns, kind, path in sorted(opts, key=lambda o: o[1] != 'item'):
            data = self.texture(ns, kind, path)
            if data:
                return data, ns
        return None


def png_size(data):
    w, h = struct.unpack('>II', data[16:24])
    return w, h
