# Map mod names as written in the guide to asset namespaces.
import json, os, re
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALIASES = {
    "alex's caves": ['alexscaves', 'alexscaves_torpedoes'], "ac": ['alexscaves'], "alex's mobs": ['alexsmobs'],
    "twilight forest": ['twilightforest', 'twilightdelight'], "twilight": ['twilightforest'], "mowzie's mobs": ['mowziesmobs'], "mowzie's": ['mowziesmobs'],
    "aquamirae": ['aquamirae'], "bosses'rise": ['block_factorys_bosses'], "betterend": ['betterend'], "betternether": ['betternether'],
    "bygone nether": ['bygonenether'], "the graveyard": ['graveyard'], "graveyard": ['graveyard'], "simply swords": ['simplyswords'],
    "artifacts": ['artifacts'], "immersive armors": ['immersive_armors'], "armor of the ages": ['armoroftheages'], "northstar": ['northstar'],
    "minecraft": ['minecraft'], "vanilla": ['minecraft'], "create": ['create'], "create nuclear": ['createnuclear'], "rftools": ['rftoolsbase', 'rftoolsutility', 'rftoolsbuilder', 'rftoolsdim'],
    "iron's spells": ['irons_spellbooks'], "ars nouveau": ['ars_nouveau'], "adam's ars plus": ['adamsarsplus'], "ars elemental": ['ars_elemental'],
    "magic from the east": ['iss_magicfromtheeast'], "refined mod": ['refined_mod'], "twilight spellbooks": ['twilight_spellbooks'],
    "apprentice's codex": ['apprenticecodex'], "alex's caves spellbooks": ['alexs_caves_spellbooks'], "dark doppelganger": ['darkdoppelganger'],
    "ars nouveau's flavors & delight": ['arsdelight'], "wind's spellbooks": ['wind_spellbooks'], "geomancy plus": ['gtbcs_geomancy_plus'],
    "farmer's spell": ['farmers_spell'], "farmer's delight": ['farmersdelight'], "supplementaries": ['supplementaries'], "dragon mounts": ['dragonmounts'],
    "immersive aircraft": ['immersive_aircraft'], "diesel generators": ['createdieselgenerators'], "power grid": ['powergrid'],
    "crafts & additions": ['createaddition'], "shield expansion": ['shieldexp'], "ac: torpedoes": ['alexscaves_torpedoes'],
    "naturalist": ['naturalist'], "spawn": ['spawn'], "croptopia": ['croptopia'], "vinery": ['vinery'], "sophisticated backpacks": ['sophisticatedbackpacks'],
}


def load_index():
    idx = json.load(open(os.path.join(D, 'modindex.json'), encoding='utf-8'))
    for x in idx:
        ALIASES.setdefault(x['name'].lower(), [x['id']])
    return idx


def hint_for(text):
    """text like "Simply Swords, rapier" or "Iron's Spells" -> namespaces"""
    first = text.split(',')[0].strip().lower()
    first = re.sub(r'\s*\(.*$', '', first)
    if first in ALIASES:
        return ALIASES[first]
    for k, v in ALIASES.items():
        if first.startswith(k):
            return v
    return None
