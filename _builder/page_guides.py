# Opening explanations for every wiki page, plus which mods' own docs to point to.
# "about": what the page covers and the ideas you need to read it. "how": optional reading notes.
# "mods": mod ids whose official wiki / project page is worth linking at the end of the page.

GUIDES = {
 'what-is-bscraft': {
  'about': [
   "BSCraft 4 is a Minecraft 1.20.1 pack built around exploring a fantasy world. Most of what makes it different is in the world itself: new biomes, a lot more structures, extra dimensions and far more bosses than vanilla. Magic and tech sit on top of that, and you can lean into either or ignore them.",
   "This page is the short version of the whole pack. The best-in-slot list is a quick pointer to the strongest things in each category, and every item in it has a full entry somewhere else in the wiki."],
  'mods': ['twilightforest', 'ars_nouveau', 'irons_spellbooks', 'create']},
 'vs-vanilla': {
  'about': [
   "If you know vanilla Minecraft, this is the list of things that will surprise you. Some come from mods (villages are replaced, bosses are tougher, chests work differently), and some are settings chosen for this server, marked as such.",
   "Read this before your first long trip. A few of these, like per-player loot and corpses, change how risky exploring really is."],
  'mods': ['lootr', 'corpse', 'waystones']},
 'quality-of-life': {
  'about': [
   "Quality-of-life mods don't add content. They take away the annoying parts, so more of your time goes into exploring and less into managing your inventory or losing items.",
   "The two that change the most are Lootr and Corpse. Lootr gives every player their own loot in every chest that came with the world, so there's no race to loot a dungeon first. Corpse keeps everything you carried when you die, safe in a body that never despawns while it holds items."],
  'mods': ['lootr', 'corpse', 'waystones', 'sophisticatedbackpacks', 'inventoryprofilesnext', 'jei']},
 'controls': {
  'about': [
   "These are the pack's default keys. The most useful habit to build early is looking things up: hover any item and press R to see how it's made, or U to see what it's used for. That shows this pack's real recipes, which sometimes differ from what the mods' wikis say.",
   "A few keys do two jobs, but only in different situations, like R opening the spell wheel on foot and dismounting inside an aircraft. If you installed the pack before the magic update, your old key settings were kept, so check Options, then Controls, if a key does nothing."],
  'mods': ['jei', 'jade', 'xaerominimap']},
 'settings': {
  'about': [
   "The pack ships with safe settings that run on most PCs. This page lists the ones people usually change, what each one costs in performance, and what the pack starts on.",
   "Shaders and far-terrain rendering look great but are the heaviest options. Turn them on one at a time and see how your PC copes."],
  'mods': ['oculus', 'distanthorizons']},
 'what-you-can-do': {
  'about': [
   "A plain overview of the activities the pack supports, grouped by type. It isn't a checklist and there's no order to it. Each line points to the part of the wiki with the details."],
  'mods': []},
 'difficulty': {
  'about': [
   "BSCraft has no questline, so this page describes the pack by how dangerous each part is and what gear usually matches it. Think of it as a rough danger map, not a route.",
   "Tiers go from normal Overworld gear up to endgame magic and space. Each tier lists the gear you'll typically find there, the magic you can reach, and the threats waiting. Only the Twilight Forest actually locks its own areas behind its bosses."],
  'mods': ['twilightforest']},
 'ways-to-play': {
  'about': [
   "A few directions people take through the pack, from exploring and boss hunting to building, engineering and magic. They aren't classes. Mix them however you like; each is just an example chain of things that lead into each other."],
  'mods': []},
 'biomes': {
  'about': [
   "Several mods add biomes to every dimension: Oh The Biomes We've Gone and Regions Unexplored cover most of the Overworld, BetterNether and BetterEnd rebuild the Nether and the End, and magic mods add a couple of their own.",
   "Biomes matter because they decide which mobs spawn and which structures can appear. Nature's Compass finds any biome by name, which is the quickest way to reach a specific one."],
  'mods': ['biomeswevegone', 'regions_unexplored', 'betternether', 'betterend', 'naturescompass']},
 'structures': {
  'about': [
   "Around twenty mods add structures, from small ruins and wells to huge dungeons, sky fortresses and wizard towers. Almost all of them use loot tables, which means their chests can roll rare items, including the Simply Swords legendaries.",
   "Because of Lootr, every chest here has its own loot for you, even in a place someone else already explored. The ranked list shows where the best loot tends to be, and how dangerous it is to get."],
  'mods': ['dungeons_arise', 'lootr', 'moogs_structures', 'irons_spellbooks']},
 'nether-end': {
  'about': [
   "Both late-game dimensions are rebuilt. The Nether gets new biomes, two metal lines and ancient structures. The End gets a harder dragon fight, new biomes, and a set of End metals that leads to Aeternium, one of the best armor sets in the pack."],
  'mods': ['betternether', 'betterend', 'bygonenether']},
 'twilight-forest': {
  'about': [
   "The Twilight Forest is a separate dimension you enter by throwing a diamond into a pool ringed with flowers. It has its own bosses, gear and a strict progression: each boss unlocks the next area, and locked areas hurt you until you've earned them.",
   "It's one of the best sources of mid-game gear, charms that save you from death, and some of the strongest ranged weapons in the pack."],
  'mods': ['twilightforest', 'twilightdelight']},
 'alexs-caves': {
  'about': [
   "Alex's Caves adds six large cave biomes deep under the Overworld, each with its own creatures, boss and gear. They're hidden: you find them by decoding cave tablets into maps.",
   "Each cave is its own little world, from magnetic ruins and candy caverns to a primordial jungle full of dinosaurs and a toxic nuclear zone."],
  'mods': ['alexscaves']},
 'space-and-vehicles': {
  'about': [
   "Rockets, planes, airships, physics ships and submarines. Northstar takes you to the Moon, Mars, Mercury and Venus; Immersive Aircraft and Valkyrien Skies cover flying and sailing around your world.",
   "Most of these are built with Create, so this page pairs well with the Create section."],
  'mods': ['northstar', 'immersive_aircraft', 'valkyrienskies']},
 'ores': {
  'about': [
   "Every modded ore in the pack, read from the world-generation files. The Y range is the height where an ore can appear, vein size is the most blocks in one vein, and attempts per chunk says how common it is.",
   "In game, JEI with JER shows the same data: look up an ore and open its distribution tab."],
  'mods': ['jeresources']},
 'bosses': {
  'about': [
   "Every boss in the pack, with the numbers taken from each mod's own code rather than from wikis, which are often out of date for this version. Health is the boss's HP, armor reduces your damage the same way yours reduces theirs, and damage is how hard its main attack hits before your armor.",
   "Tiers are a rough overall rating that weighs health, damage, mechanics and how hard the boss is to reach. Dying to a boss is less painful than you'd think: your items wait in your corpse in the arena."],
  'how': "Click a column name to sort. Type in the filter to narrow the list by name, mod or tier letter.",
  'mods': ['mowziesmobs', 'block_factorys_bosses', 'graveyard', 'aquamirae', 'darkdoppelganger']},
 'weapons': {
  'about': [
   "Every notable melee weapon on one scale. Damage is what the tooltip shows. Speed is attacks per second. DPS is damage times speed, which is your sustained damage if every hit lands at full charge.",
   "Heavy weapons win on single big hits, fast weapons win on damage over time, and a weapon's special ability often matters more than either. Enchantments change the picture too: Sharpness adds a flat bonus per hit, which helps fast weapons the most (see Enchantments)."],
  'how': "Click a column name to sort, for example by DPS. Type in the filter to find a weapon, a mod, or a tier letter.",
  'mods': ['simplyswords', 'irons_spellbooks', 'aquamirae']},
 'ranged': {
  'about': [
   "Bows, beam guns, staffs, gauntlets, summoning items and machine weapons. They don't share a single damage formula, so they're described by what they do and how strong that is in practice. Spells themselves are covered in the Magic section."],
  'mods': ['alexscaves', 'twilightforest']},
 'armor': {
  'about': [
   "Every full armor set on one scale. Armor is the set total; vanilla netherite is 20. Toughness is listed per piece, and it matters most against big hits: the harder something hits, the more your armor gets worn through, and toughness slows that down.",
   "Knockback resistance stops you getting launched. Chest durability is a good guide to how long a set lasts. The pack raises the usual caps, so armor above 30 and toughness above 20 still count."],
  'how': "Click a column name to sort. The Enchantments page shows how much damage each set actually lets through, with and without Protection.",
  'mods': ['betterend', 'immersive_armors', 'adamsarsplus']},
 'enchantments': {
  'about': [
   "Enchanting works like vanilla: a table, an anvil and books. On top of the vanilla enchantments you get 37 more from Ensorcellation, plus item-specific ones from other mods.",
   "The first half of this page shows how enchantments change the weapon and armor comparisons, with real numbers. Protection IV on every piece removes about two thirds of the damage that gets past your armor, so the gap between armor sets shrinks once everything is enchanted."],
  'mods': ['ensorcellation', 'enchdesc']},
 'powers': {
  'about': [
   "Every way to give your character extra abilities: flight, double jumps, cheating death, damage boosts, summons and more. Most of these are accessories that go in curio slots (G), so they stack with your armor.",
   "The Artifacts list shows which structures each accessory can appear in, with the chance per chest."],
  'mods': ['artifacts', 'curios']},
 'getting-gear': {
  'about': [
   "Full crafting chains for the major gear, traced back to where each ingredient comes from: an ore, a mob drop, a structure chest or a boss. JEI shows the exact crafting grid in game (R on the item).",
   "The upgrade ladder at the end suggests a realistic order for each armor slot, from early game to endgame."],
  'mods': ['jei']},
 'magic': {
  'about': [
   "Two complete magic systems run side by side. Ars Nouveau lets you build your own spells from pieces called glyphs and automate things with rituals and helper creatures. Iron's Spells 'n Spellbooks works like an RPG: you find spells as scrolls, level them up and cast them from a spellbook.",
   "They share one mana bar, so casting from either system draws from the same pool. Spell power from your gear boosts both, and keeping your mana nearly full gives a small damage bonus."],
  'mods': ['ars_nouveau', 'irons_spellbooks', 'ars_n_spells']},
 'ars-nouveau': {
  'about': [
   "In Ars Nouveau a spell is a chain of glyphs. It starts with a form (how the spell travels, like a projectile or a touch), then one or more effects (what it does, like harm or break), with augments that change the glyph right before them (stronger, wider, longer).",
   "Source is the mod's magic resource, made by Sourcelinks and moved around with jars and relays. It powers crafting, rituals and the helper creatures that farm, craft and haul items for you. Addons add more glyphs, armor, bosses and whole new schools."],
  'mods': ['ars_nouveau', 'ars_elemental', 'adamsarsplus']},
 'irons-spells': {
  'about': [
   "Iron's Spells gives you nine schools of magic with over a hundred spells. Every spell has a level, a mana cost and a cooldown. Higher-level scrolls come from better ink, and your spell power (from armor, rings and books) makes every spell hit harder.",
   "You collect spells as scrolls from chests and spellcasting mobs, inscribe them into a spellbook at the Inscription Table, and cast from the spell wheel. Addons add new schools, from wind and earth to eastern spirit magic."],
  'mods': ['irons_spellbooks', 'iss_magicfromtheeast', 'apprenticecodex']},
 'villagers': {
  'about': [
   "Villagers here are people rather than shops with legs, and that changes how villages feel more than any other mod in this update.",
   "If all you want is trading, nothing has changed: jobs, workstations and prices work the way they always did. Everything below is the part you can take or leave."],
  'mods': ['mca']},
 'creatures': {
  'about': [
   "Five animal and monster mods add well over 150 creatures. Alex's Mobs matters most, because many of its drops craft real gear. This page covers the gear you get from creatures and the mobs worth knowing about."],
  'mods': ['alexsmobs', 'naturalist', 'mowziesmobs']},
 'mounts': {
  'about': [
   "Everything you can tame, ride or bring along, grouped by mod, with what each one eats and what it's good for. Magic adds summoned mounts, familiars and helpers on top."],
  'mods': ['alexsmobs', 'alexscaves', 'dragonmounts']},
 'bestiary': {
  'about': [
   "Every regular creature, with health, damage and armor read from each mod's own code and drops from its loot tables. Blank stats mean the mob uses vanilla defaults. Bosses have their own page.",
   "It's long, so the search at the top is the fastest way to find a mob."],
  'mods': ['alexsmobs', 'mowziesmobs', 'naturalist']},
 'create': {
  'about': [
   "Create is a tech mod built around rotation: water wheels, windmills and engines produce rotational force, and shafts and gears carry it to machines. Its addons add electricity, trains, diesel, nuclear power and more.",
   "The page walks through the material ladder, every power source compared, and the extras that tie Create into the rest of the pack."],
  'mods': ['create', 'createaddition', 'createnuclear', 'railways']},
 'rftools': {
  'about': [
   "RFTools adds powerful utility machines that run on Forge Energy: teleporters, builders and quarries, crafting automation, and the Environmental Controller, which can give everyone in your base flight, regeneration or no hostile spawns. Bigger Reactors is the big power source to feed them."],
  'mods': ['rftoolsutility', 'rftoolsbuilder', 'rftoolsdim', 'biggerreactors']},
 'systems': {
  'about': [
   "Step-by-step explanations for the bigger systems: the waystone network, backpacks and their upgrades, trains, programmable computers, and a few mod-specific mechanics like biome conversion and Deep One trading."],
  'mods': ['waystones', 'sophisticatedbackpacks', 'computercraft', 'supplementaries']},
 'food': {
  'about': [
   "Food in this pack works a lot like potions. Farmer's Delight meals give two core buffs: Nourishment (your hunger stops draining) and Comfort (you regenerate at any hunger level). Drinks, wines and themed dishes add real combat effects, and some magic drinks refill your mana.",
   "Wine from Vinery gets stronger as it ages, up to five effect levels."],
  'mods': ['farmersdelight', 'vinery', 'brewinandchewin', 'croptopia']},
 'building': {
  'about': [
   "Decoration and gadget mods: furniture, thousands of block variants, useful devices like quivers, slingshots and jars, bigger chests and storage."],
  'mods': ['supplementaries', 'chipped', 'mcwfurnitures', 'handcrafted']},
 'combos': {
  'about': [
   "Two or three mods lining up to do something none of them does alone. None of this is required, and none of it is in any particular order.",
   "If you only want one thing from this page: rotation and electricity are different currencies, and knowing which mod converts between them saves a lot of confusion later."],
  'mods': ['create', 'create_enchantment_industry', 'ars_nouveau', 'fallingtree', 'waystones']},
 'multiplayer': {
  'about': [
   "What changes when other people are on the server. Most of it is about loot, corpses and what other players can take.",
   "The short version: your loot is your own, your corpse is not, and PvP is on."],
  'mods': ['lootr', 'corpse', 'waystones']},
 'changelog': {
  'about': [
   "What changed in the pack, newest first, limited to the things that affect how you play."],
  'mods': []},
 'read-more': {
  'about': [
   "The mods' own wikis and docs go much deeper than this wiki can. They're sometimes written for other versions, so trust this wiki or the in-game tooltip for numbers, and use these for how things work."],
  'mods': []},
}
