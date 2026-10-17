"""Reactive Crafting animations (tools/build_fx.py): the 11 throwables get a flying projectile + a terrain-specific impact,
built from core_2 templates with neutral (tint-clean) particle tiles. Only the game's particle atlas is used.

    python tools/build_fx.py            writes animations/*.json and sets each ability's `animation`
"""
import copy
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = Path(os.environ.get("S2_CORE_ANIMATIONS") or ROOT.parent / "core_2" / "animations")
P = "arendeth_reactive_crafting_"

def vanilla(stem):
    for f in CORE.iterdir():
        if f.stem == stem or f.stem.startswith(stem + "_"):
            return json.load(open(f, encoding="utf-8-sig"))
    raise FileNotFoundError(stem)

T = {k: vanilla(k) for k in ("3_Fireball", "4_Fireball_explosion", "61_Flame_nova", "65_Phaseshift", "Frost_armor", "15_Whirlwind")}

# neutral tile sets (tint cleanly): mapping of the 9 explosion-template ids -> new ids, per flavour
EXPL_SRC = [376, 377, 378, 379, 380, 381, 382, 383, 364]
FLAVOUR = {
    "sparkle": [65, 66, 67, 68, 69, 1343, 1344, 1345, 1346],
    "frost":   [553, 554, 555, 556, 557, 1344, 1345, 1346, 554],
    "smoke":   [545, 546, 547, 548, 549, 550, 551, 1344, 546],
    "lines":   [65, 66, 1297, 1298, 1299, 1300, 1301, 1302, 1343],
    "ring":    [743, 744, 745, 746, 745, 744, 743, 1344, 1345],
    "glitch":  [1386, 1387, 1388, 1389, 1390, 1391, 1387, 1344, 1345],
    "heal":    [65, 66, 67, 1193, 1194, 1195, 1196, 1197, 1344],
    "death":   [49, 50, 51, 52, 53, 1344, 1345, 1346, 1343],
}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

def tint(parts, rgb, alpha=None):
    for p in parts:
        rows = p.get("color") or [[255, 255, 255, 255]]
        new = []
        for row in rows:
            a = row[3] if len(row) > 3 else 255
            new.append([rgb[0], rgb[1], rgb[2], a if alpha is None else alpha])
        p["color"] = new

def remap(parts, mapping):
    for p in parts:
        p["tile_id"] = mapping.get(p.get("tile_id"), p.get("tile_id"))

def shake(a, power):
    a["camera_shake"] = {"bounces": 4 if power else 2, "duration": 0.25 if power else 0.0, "power": power, "type": 1}

def clamp_range(parts, r):
    for p in parts:
        if "explosion_range" in p:
            p["explosion_range"] = max(1, min(int(p["explosion_range"]), r))

def base(id_, name, tmpl, parts, sound=None, power=0, chain=None):
    a = {k: copy.deepcopy(v) for k, v in tmpl.items() if k != "particles"}
    a["id"] = P + id_
    a["name"] = name
    a["particles"] = parts
    if sound:
        a["sound"] = {"id": sound, "volume": 100}
    if chain is not None:
        a["chain_particles"] = chain
    shake(a, power)
    return a

def hit(id_, name, rgb, flavour, rng, power, sound="13"):
    parts = copy.deepcopy(T["4_Fireball_explosion"]["particles"])
    remap(parts, dict(zip(EXPL_SRC, FLAVOUR[flavour])))
    tint(parts, rgb)
    clamp_range(parts, rng + 1)
    return base(id_, name, T["4_Fireball_explosion"], parts, sound=sound, power=power, chain=False)

BOLT_MAP = dict(zip([390, 391, 392, 393, 394, 395, 396, 397, 398, 399], [65, 66, 67, 68, 69, 68, 67, 66, 65, 67]))
def bolt(id_, name, rgb, hit_id, small=False):
    parts = copy.deepcopy(T["3_Fireball"]["particles"])
    remap(parts, BOLT_MAP)
    tint(parts, rgb)
    parts[-1]["on_impact"] = P + hit_id          # the flying particle hands over to the impact
    if small:
        parts = parts[:3] + parts[-1:]
    return base(id_, name, T["3_Fireball"], parts, sound="10", power=0, chain=True)

def aura(id_, name, rgb):
    parts = copy.deepcopy(T["Frost_armor"]["particles"])
    remap(parts, dict(zip([928, 929, 930, 931, 932, 933, 934], [743, 744, 745, 746, 1343, 1344, 1345])))
    tint(parts, rgb)
    return base(id_, name, T["Frost_armor"], parts, sound="35", power=0, chain=True)

def conjure(id_, name, rgb):
    parts = [p for p in copy.deepcopy(T["65_Phaseshift"]["particles"]) if not p.get("on_impact")]
    remap(parts, dict(zip([523, 522, 520, 519, 518, 517, 516, 515, 514, 513, 524], [65, 66, 67, 68, 67, 66, 65, 1344, 1345, 1346, 1343])))
    tint(parts, rgb)
    return base(id_, name, T["65_Phaseshift"], parts, sound="62", power=0, chain=True)

def nova(id_, name, rgb, flavour="ring", big=False):
    parts = copy.deepcopy(T["61_Flame_nova"]["particles"])
    ids = {"ring": [743, 744, 745], "sparkle": [67, 68, 69], "lines": [1297, 1298, 1299]}[flavour]
    remap(parts, dict(zip([561, 562, 563], ids)))
    extra = copy.deepcopy(parts[-1]); extra["tile_id"] = 746 if flavour == "ring" else ids[-1]
    extra["delay"] = 150.0; extra["explosion_range"] = parts[-1]["explosion_range"] + 1
    parts.append(extra)
    if big:
        for p in parts: p["explosion_range"] += 1
    tint(parts, rgb)
    return base(id_, name, T["61_Flame_nova"], parts, sound="13", power=0, chain=False)

def whirl(id_, name, rgb):
    parts = copy.deepcopy(T["15_Whirlwind"]["particles"])
    remap(parts, {606: 752, 450: 753})
    tint(parts, rgb)
    return base(id_, name, T["15_Whirlwind"], parts, sound="20", power=0, chain=False)


# ---- the plan: each throwable -> (flavour for the impact, impact tint, projectile tint, camera power) -----------------
# "native" keeps the vanilla Fireball explosion tiles (already fire-coloured); other flavours use neutral tiles + tint.
PLAN = {
    "Throw_Muddy_Waterskin":     ("smoke",   (118, 84, 48),   (140, 100, 60),  1),
    "Throw_Sand_Pouch":          ("grain",   (232, 198, 122), (235, 205, 140), 1),
    "Throw_Ember_Pouch":         ("native",  (255, 170, 80),  (255, 150, 50),  2),
    "Throw_Snow_Pouch":          ("frost",   (205, 228, 248), (220, 238, 250), 1),
    "Throw_Oil_Flask":           ("lines",   (225, 222, 205), (150, 120, 70),  1),
    "Throw_Salt_Sack":           ("frost",   (244, 244, 234), (250, 250, 240), 1),
    "Throw_Greater_Ember_Pouch": ("native",  (255, 205, 120), (255, 190, 90),  4),
    "Throw_Quagmire_Skin":       ("smoke",   (78, 82, 44),    (95, 100, 55),   2),
    "Throw_Glacial_Pouch":       ("frost",   (150, 205, 255), (180, 220, 255), 3),
    "Throw_Brine_Flask":         ("smoke",   (118, 200, 178), (140, 215, 195), 1),
    "Throw_Volatile_Bundle":     ("sparkle", (255, 190, 90),  (255, 220, 140), 5),
}

FLAVOUR["grain"] = [1065, 1066, 1067, 1068, 1069, 1344, 1345, 1346, 1066]   # grainy spray: sand

def hit_native(id_, name, rgb, rng, power):
    parts = copy.deepcopy(T["4_Fireball_explosion"]["particles"])
    tint(parts, rgb)
    clamp_range(parts, rng + 1)
    return base(id_, name, T["4_Fireball_explosion"], parts, sound="13", power=power, chain=False)

abil = {}
for f in (ROOT / "abilities").glob("*.json"):
    a = json.load(open(f, encoding="utf-8-sig"))
    abil[a["id"]] = a

anims, fx = {}, {}
for key, (flav, hrgb, brgb, power) in PLAN.items():
    aid = P + key
    if aid not in abil:
        print("skip (no ability):", key)
        continue
    name = abil[aid]["name"]
    rng = int((abil[aid].get("effects") or {}).get("aoe_range", 2))
    hid = f"{slug(name)}_fx_hit"
    h = hit_native(hid, f"{name} FX Hit", hrgb, rng, power) if flav == "native" else hit(hid, f"{name} FX Hit", hrgb, flav, rng, power)
    b = bolt(f"{slug(name)}_fx", f"{name} FX", brgb, hid)
    anims[h["id"]] = h
    anims[b["id"]] = b
    fx[aid] = b["id"]

(ROOT / "animations").mkdir(exist_ok=True)
for i, a in anims.items():
    (ROOT / "animations" / f"{i[len(P):]}.json").write_text(json.dumps(a, indent="\t") + "\n", encoding="utf-8")
patched = 0
for f in (ROOT / "abilities").glob("*.json"):
    a = json.load(open(f, encoding="utf-8-sig"))
    if a.get("id") in fx and a.get("animation") != fx[a["id"]]:
        a["animation"] = fx[a["id"]]
        f.write_text(json.dumps(a, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
        patched += 1
print("wrote", len(anims), "animations, patched", patched, "abilities")

if "--preview" in sys.argv:
    sys.path.insert(0, r"D:\games\Ai assisted toolkit\Tools\Soulash2\SkillCreator")
    os.chdir(r"D:\games\Ai assisted toolkit\Tools\Soulash2\SkillCreator")
    from s2_fx_preview import write_preview_pack
    root = Path(r"D:\games\Ai assisted toolkit\Tools\Output\Soulash2\_fx_preview\reactive_crafting")
    for key in PLAN:
        a = anims.get(fx.get(P + key, ""))
        if a:
            write_preview_pack(a, root / key, extras=[x for i, x in anims.items() if i == a["id"] + "_hit"])
            print("preview", key)
