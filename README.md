# BSCraft 4 wiki

The player wiki for the BSCraft 4 modpack (Minecraft 1.20.1, Forge 47.4.10, 256 mods).

It is a static site: open `index.html` in a browser, or upload the root of this repo to any static host. Nothing runs on the server.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `assets/`, `images/` | the built site |
| `_builder/BSCraft-4-Guide.md` | the guide text every page is built from |
| `_builder/build_wiki.py` | builds the site out of the guide, the mod jars and the mod index |
| `_builder/modindex.json` | every mod in the pack: id, jar, category, one-line description |
| `_builder/modmeta.json` | each mod's links and author blurb (Modrinth matched by file hash) |
| `_builder/page_guides.py` | the opening explanation and further reading for each page |
| `_builder/src/` | page shell, stylesheet and front-end script |
| `_builder/theme/` | the menu art the site is styled from |

## Rebuilding

Needs Python 3.11+ and a copy of the modpack, since item icons and mod logos are read straight from the jars.

```
cd _builder
python build_wiki.py
```

`build_wiki.py` expects `BSCraft-4-Guide.md` and `modindex.json` one level above it, and writes the site to `site/`. `modmeta.py` refreshes the mod links, `make_zip.py` packs the site for upload.

## Where the facts come from

Everything is taken from the pack's own files: recipes, loot tables, configs, and the mods' own code for boss and item stats. Mod wikis are used for explanations, not numbers. Where the two disagree, the pack wins.

## Credits

Item icons and mod logos belong to their mods' authors. Screenshots keep their source credit on the page that shows them. The background and menu art come from the pack's main menu theme.
