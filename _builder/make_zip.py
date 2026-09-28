# Packs site/ into Documents\BSCraft-Wiki.zip for upload to a static host.
# Entries use forward slashes so the folders survive unzipping on Linux hosts (Netlify, GitHub Pages, Cloudflare Pages).
import os, zipfile

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
OUT = os.path.join(os.path.expanduser('~'), 'Documents', 'BSCraft-Wiki.zip')
BS = chr(92)

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for root, dirs, files in os.walk(SITE):
        dirs.sort()
        for f in sorted(files):
            path = os.path.join(root, f)
            z.write(path, os.path.relpath(path, SITE).replace(os.sep, '/'))

with zipfile.ZipFile(OUT) as z:
    names = z.namelist()
    broken = z.testzip()
print(f'{len(names)} files, {sum(BS in n for n in names)} with backslashes, test: {broken or "ok"}, {os.path.getsize(OUT) / 1048576:.1f} MB')
print('top level:', sorted({n.split("/")[0] for n in names}))
