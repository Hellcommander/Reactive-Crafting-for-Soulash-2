"""Apply the Reactive Crafting asset + learning-method changes to a mod folder (a scratch copy, then the live mod).

usage: rc_apply.py <mod_dir> [--assets <staging assets dir>]
  - declares skills/abilities/passive_skills/items/glyph32 sheets in assets.json (matching the PNGs actually present)
  - gives every throwable its own item + glyph tile (indices 0-10) and the Manual tile 11
  - adds the craftable Reactive Crafting Manual (usable.skill_p) + its recipe milestone at skill level 10
  - adds craft/throw exp sources and the manual to skills.json; version/description in mod.json
"""
import json
import shutil
import sys
from pathlib import Path

mod = Path(sys.argv[1])
assets_src = Path(sys.argv[sys.argv.index("--assets") + 1]) if "--assets" in sys.argv else None
SK = "arendeth_reactive_crafting"
P = SK + "_"
MANUAL = P + "Reactive_Crafting_Manual"

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

def save(p, o, nl=True):
    Path(p).write_text(json.dumps(o, indent="\t", ensure_ascii=False) + ("\n" if nl else ""), encoding="utf-8")

# ---- 0. copy staged art in (when given) --------------------------------------------------------------------------
if assets_src:
    (mod / "assets").mkdir(exist_ok=True)
    for name in ("abilities.png", "passive_skills.png", "items.png", "glyphs.png", "skills.png"):
        s = assets_src / "assets" / name
        if s.exists():
            shutil.copy2(s, mod / "assets" / name)
    for name in ("icon.png", "thumbnail2.png"):
        s = assets_src / name
        if s.exists():
            shutil.copy2(s, mod / name)
    if (assets_src / "icon.png").exists():
        shutil.copy2(assets_src / "icon.png", mod / "S.png")     # legacy duplicate some tools still read

# ---- 1. assets.json: only declare sheets whose PNG exists, with the real cell counts ----------------------------------
from PIL import Image  # noqa: E402

NO_SHEETS = "--no-sheets" in sys.argv     # art not ready yet: leave assets.json and item/glyph indices alone

def cells(png, cell):
    im = Image.open(mod / png)
    return [im.width // cell, im.height // cell]

if not NO_SHEETS:
    sheets = []
    for name, png, cell in (("skills", "assets/skills.png", 32), ("abilities", "assets/abilities.png", 32),
                            ("passive_skills", "assets/passive_skills.png", 32), ("items", "assets/items.png", 32),
                            ("glyph32", "assets/glyphs.png", 16)):
        if (mod / png).exists():
            sheets.append({"name": name, "tiles": cells(png, cell), "file": png})
    save(mod / "assets.json", {"graphics": {"tilesheets": sheets}})
    print("assets.json sheets:", [(s["name"], s["tiles"]) for s in sheets])
else:
    print("--no-sheets: assets.json and item/glyph indices left untouched")

# ---- 2. distinct item + glyph tiles per throwable ----------------------------------------------------------------------
ORDER = ["Muddy_Waterskin", "Sand_Pouch", "Ember_Pouch", "Snow_Pouch", "Oil_Flask", "Salt_Sack",
         "Greater_Ember_Pouch", "Quagmire_Skin", "Glacial_Pouch", "Brine_Flask", "Volatile_Bundle"]
has_items = (mod / "assets" / "items.png").exists() and not NO_SHEETS
for idx, ent in enumerate(ORDER):
    f = mod / "entities" / f"{ent}.json"
    j = load(f)
    if has_items:
        j.setdefault("item", {})["image"] = idx
        fr = j.setdefault("glyph", {}).setdefault("frames", [{}])
        fr[0]["index"] = idx
        if len(fr[0].get("color") or []) == 4:
            fr[0]["color"] = [255, 255, 255, 255]
        else:
            fr[0]["color"] = [255, 255, 255]       # variants have their own art now: no tint
    save(f, j)

# ---- 3. the Manual (player-built skill book) -----------------------------------------------------------------------------
manual = {
    "components": ["craftable", "glyph", "item", "minimap_pixel", "name", "position_2d", "stackable", "usable", "value", "weight"],
    "craftable": {"backgrounds": [], "biomes": [], "cooldown": 432000, "magic_slots": 0,
                  "resources": [{"amount": 1, "id": "2006"}, {"amount": 1, "id": P + "Muddy_Waterskin"}],
                  "time": 60, "tools": []},
    "description": "A hand-stitched training manual of terrain-reactive crafting: how to read the ground, pack a pouch for it, and throw it true. Studying it raises your Reactive Crafting potential. Bind one from a Book and a Muddy Waterskin for practice.",
    "glyph": {"frames": [{"color": [255, 255, 255], "delay": 0, "index": 11 if has_items else 2975}], "random_frame_start": False},
    "id": MANUAL,
    "item": {"image": 11 if has_items else 1359, "type": 17},
    "minimap_pixel": [200, 160, 100],
    "name": "Reactive Crafting Manual",
    "usable": {"ability": "", "recipe": "", "skill_p": SK},
    "value": 3000,
    "weight": 0.2,
}
save(mod / "entities" / "Reactive_Crafting_Manual.json", dict(sorted(manual.items())))

mdir = mod / "milestones" / SK
mdir.mkdir(parents=True, exist_ok=True)
save(mdir / "10_Craft_Reactive_Crafting_Manual.json",
     {"id": MANUAL + "_recipe", "name": "Craft Reactive Crafting Manual",
      "requirements": {"milestones": [], "skill": 10}, "rewards": [{"recipe": MANUAL}],
      "skill_id": SK, "steps": [], "steps_type": 0})

# ---- 4. skills.json: more ways to gain experience + say how to go past 10 -------------------------------------------
sk = load(mod / "skills.json")
s0 = sk[0]
src = {e["id"]: e for e in s0.get("exp_sources", [])}
src.setdefault("ability", {"id": "ability", "rate": 2})
src["craft"] = {"id": "craft", "rate": 1}
src["throw"] = {"id": "throw", "rate": 2}
s0["exp_sources"] = list(src.values())
desc = s0["description"]
if "Manual" not in desc:
    desc = desc.replace("Train by throwing what you craft.",
                        "Train by crafting and throwing what you make.\n\nYou start at level 10. To go further, study a Reactive Crafting Manual: you can build one from a Book and a Muddy Waterskin once you reach level 10, and each one raises your potential.")
s0["description"] = desc
save(mod / "skills.json", sk)

# ---- 5. mod.json ----------------------------------------------------------------------------------------------------------
m = load(mod / "mod.json")
m["version"] = "0.7.0"
m["icon"] = "icon.png"
m["thumbnail"] = "thumbnail2.png"
m["description"] = ("Adds Reactive Crafting, a 20-level utility skill. Level up to unlock the recipes for terrain-reactive craftable "
                    "throwables (muddy waterskins, sand pouches, salt sacks, snow pouches, ember pouches, oil flasks), improved versions, "
                    "and the Volatile Bundle. Build Reactive Crafting Manuals to raise your potential past level 10. "
                    "No statistics for levels 1-10.")
save(mod / "mod.json", m)
print("applied to", mod)
