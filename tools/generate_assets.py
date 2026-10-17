"""Reactive Crafting real-asset job (STAGING only; nothing is written into the live mod).

usage: rc_assets.py clean | gen [--only kind] | pack
  clean : strip the mismatched backgrounds from the existing 32px ability/item tiles (no GPU)
  gen   : SD3.5 (toolkit pipeline) for the missing tiles; one PNG per tile, resumable
  pack  : assemble sheets + icon + thumbnail into the staging folder and write a contact sheet
Sheets are 32px cells (abilities, passives, skills, items) and 16px (glyph32), as vanilla and the workshop mods use.
"""
import os
import sys
from pathlib import Path

TOOLS = Path(r"D:\games\Ai assisted toolkit\Tools")
sys.path.insert(0, str(TOOLS / "Soulash2" / "SkillCreator"))
sys.path.insert(0, str(TOOLS / "Soulash2"))
sys.path.insert(0, str(TOOLS / "Shared"))
os.environ.setdefault("AAMT_SD_KEEP_SERVER", "1")
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

LIVE = Path(r"E:\SteamLibrary\steamapps\common\Soulash 2\data\mods\arendeth_reactive_crafting")
STAGE = TOOLS / "Output" / "Soulash2" / "arendeth_reactive_crafting_assets"
TILES = STAGE / "tiles"
TILES.mkdir(parents=True, exist_ok=True)
T = 32

ITEMS = [  # index, name, concept
    (0, "Muddy Waterskin", "a stoppered leather waterskin sloshing with thick brown mud, drips on the side"),
    (1, "Sand Pouch", "a canvas pouch spilling a little pile of golden desert sand"),
    (2, "Ember Pouch", "a smoldering cloth pouch glowing with orange embers, ash and a thread of smoke"),
    (3, "Snow Pouch", "a frost-rimmed pouch packed with pale snow and tiny ice crystals"),
    (4, "Oil Flask", "an amber glass flask of dark transmutation oil, corked, a glint of light"),
    (5, "Salt Sack", "a coarse white salt sack tied with twine, grains spilling"),
    (6, "Greater Ember Pouch", "a large reinforced pouch blazing with bright molten embers and stitched runic seams"),
    (7, "Quagmire Skin", "a swollen leather skin dripping thick black-green bog mud, wet and heavy"),
    (8, "Glacial Pouch", "a pouch encased in blue glacial ice with drifting frost mist"),
    (9, "Brine Flask", "a glass flask of cloudy sea-green brine with a crust of white salt around the cork"),
    (10, "Volatile Bundle", "a bundle of mixed flasks and pouches bound with rope, sparking and unstable"),
    (11, "Reactive Crafting Manual", "a hand-stitched leather training manual with a flask emblem on the cover, tied with twine, a ribbon bookmark"),
]
ABILITIES = [
    (0, "Throw Muddy Waterskin", "a thrown waterskin bursting into brown mud splashes and wet puddles"),
    (1, "Throw Sand Pouch", "a thrown pouch bursting into a blinding golden sand cloud"),
    (2, "Throw Ember Pouch", "a thrown pouch bursting into burning ground, sparks and flames"),
    (3, "Throw Snow Pouch", "a thrown pouch bursting into snow and sharp ice crystals on the ground"),
    (4, "Throw Oil Flask", "a thrown flask shattering into sticky dark oil and sprawling cobwebs"),
    (5, "Throw Salt Sack", "a thrown sack bursting into a drifting cover of dry white salt"),
    (6, "Throw Greater Ember Pouch", "a thrown pouch bursting into a huge ring of roaring flames and embers"),
    (7, "Throw Quagmire Skin", "a thrown skin bursting into a wide pit of thick black bog mud with bubbles"),
    (8, "Throw Glacial Pouch", "a thrown pouch bursting into a field of glacial ice spikes and frost"),
    (9, "Throw Brine Flask", "a thrown flask bursting into salt spray and sea-green brine splash"),
    (10, "Throw Volatile Bundle", "a thrown bundle exploding in a mixed blast of fire, ice, sand and mud"),
]
PASSIVES = [
    (0, "Field Pack", "a rugged field backpack with flask loops and a bedroll"),
    (1, "Thrifty Hands", "a pair of hands carefully saving a few coins and a pinch of reagent"),
    (2, "Efficient Crafting", "a crafting bench with a mallet and neatly sorted tools"),
    (3, "Terrain Reader", "a watchful eye above layered ground strata of mud sand and stone"),
    (4, "Pack Mule", "a sturdy pack mule loaded with sacks and flasks"),
    (5, "Resourceful", "a hand pulling a bonus gemstone out of a handful of dirt"),
    (6, "Practiced Hands", "two calloused hands mid-craft, tying a pouch shut"),
    (7, "Steady Throw", "an arm in mid-throw with a straight motion line and a flask"),
    (8, "Deep Pockets", "an open coat pocket glowing softly from deep inside, flasks peeking out"),
    (9, "Reactive Crafting Mastery", "a golden crowned flask surrounded by four terrain swatches mud sand ember snow"),
]
SKILL = (0, "Reactive Crafting", "a thrown alchemical flask bursting into four elemental terrains mud ember snow sand, bold school emblem")
ICON = "a corked amber alchemical flask over four soft terrain blobs of mud, ember, snow and sand, bold mod icon"
THUMB = ("Soulash 2 workshop banner painting, a dark dungeon crafting bench with thrown alchemical flasks and pouches "
         "bursting into mud, sand, glowing embers and snow on the stone floor, warm earthy palette, painterly, no text")

def prompt(role, concept):
    from s2_icon_pipeline import compose_icon_prompt
    return compose_icon_prompt(role=role, subject=f"for the Reactive Crafting utility school, {concept}, single centered subject isolated on a pure black background, earthy warm palette")

def clean_tile(img, bg=(0, 0, 0, 0)):
    from s2_icon_pipeline import knockout_edge_canvas, knockout_near_black
    rgba = knockout_edge_canvas(knockout_near_black(img.convert("RGBA")))
    canvas = Image.new("RGBA", rgba.size, bg)
    canvas.paste(rgba, (0, 0), rgba)
    return canvas

def tile_path(kind, i):
    return TILES / f"{kind}_{i:02d}.png"

def old_tiles(sheet, n):
    im = Image.open(LIVE / "assets" / sheet).convert("RGBA")
    return [im.crop((i * T, 0, (i + 1) * T, T)) for i in range(min(n, im.width // T))]

mode = sys.argv[1] if len(sys.argv) > 1 else "clean"

if mode == "clean":
    # existing painterly tiles: abilities 0-5, items 0-5 (items sheet is 6 wide); drop the grey/black/gradient canvases
    for i, t in enumerate(old_tiles("abilities.png", 6)):
        clean_tile(t, bg=(22, 22, 26, 255)).save(tile_path("ability", i))
    for i, t in enumerate(old_tiles("items.png", 6)):
        clean_tile(t, bg=(0, 0, 0, 0)).save(tile_path("item", i))
    print("cleaned existing tiles into", TILES)

elif mode == "gen":
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    from s2_icon_pipeline import generate_sd_tile, sd_session, seed_from_name
    jobs = []
    for i, n, c in ITEMS:
        jobs.append(("item", i, n, prompt("inventory item icon", c), (0, 0, 0, 0)))
    for i, n, c in ABILITIES:
        jobs.append(("ability", i, n, prompt("active ability icon", c), (22, 22, 26, 255)))
    for i, n, c in PASSIVES:
        jobs.append(("passive", i, n, prompt("passive trait icon", c), (22, 22, 26, 255)))
    jobs.append(("skill", 0, SKILL[1], prompt("skill school emblem", SKILL[2]), (22, 22, 26, 255)))
    jobs.append(("icon", 0, "Mod icon", prompt("mod folder icon", ICON), (22, 22, 26, 255)))
    jobs = [j for j in jobs if (only is None or j[0] == only) and not tile_path(j[0], j[1]).exists()]
    print(f"{len(jobs)} tiles to generate", flush=True)
    work = STAGE / "_sd_work"; work.mkdir(exist_ok=True)
    with sd_session(use_sd=True) as api:
        for n, (kind, i, name, pr, bg) in enumerate(jobs, 1):
            print(f"[{n}/{len(jobs)}] {kind} {i} {name}", flush=True)
            img = generate_sd_tile(pr, work=work, api_url=api, seed=seed_from_name(name), steps=24, size=T, name=f"rc:{kind}:{name}", bg=bg)
            img.save(tile_path(kind, i))
        # thumbnail: banner profile, composited with the title afterwards in `pack`
        thumb = STAGE / "thumb_raw.png"
        if not thumb.exists() and (only in (None, "thumb")):
            from sd_http_client import generate_image, plan_sd_size
            gw, gh, st = plan_sd_size(800, 600, kind="banner")
            print(f"[thumb] {gw}x{gh} @ {st}", flush=True)
            generate_image(THUMB, thumb, api_url=api, negative_prompt="text, letters, watermark, logo, photograph, UI",
                           width=gw, height=gh, steps=st, guidance_scale=7.0, seed=seed_from_name("rc-thumb"))
    print("gen done", flush=True)

elif mode == "pack":
    def get(kind, i, size=T):
        p = tile_path(kind, i)
        return Image.open(p).convert("RGBA") if p.exists() else None
    def sheet(kind, count, name, cell=T):
        im = Image.new("RGBA", (count * cell, cell), (0, 0, 0, 0))
        missing = []
        for i in range(count):
            t = get(kind, i)
            if t is None:
                missing.append(i); continue
            if t.size != (cell, cell):
                t = t.resize((cell, cell), Image.Resampling.LANCZOS)
            im.paste(t, (i * cell, 0), t)
        out = STAGE / "assets"; out.mkdir(exist_ok=True)
        im.save(out / name)
        print(f"{name}: {count} cells @ {cell}px, missing {missing}")
        return im
    ab = sheet("ability", 11, "abilities.png")
    ps = sheet("passive", 10, "passive_skills.png")
    it = sheet("item", 11, "items.png")
    # in-world glyphs: 16px downscales of the item art
    gl = Image.new("RGBA", (11 * 16, 16), (0, 0, 0, 0))
    for i in range(11):
        t = get("item", i)
        if t is not None:
            t = t.resize((16, 16), Image.Resampling.LANCZOS); gl.paste(t, (i * 16, 0), t)
    (STAGE / "assets").mkdir(exist_ok=True); gl.save(STAGE / "assets" / "glyphs.png"); print("glyphs.png: 11 cells @ 16px")
    sk = get("skill", 0)
    if sk is not None:
        sk.save(STAGE / "assets" / "skills.png"); print("skills.png ok")
    ic = get("icon", 0)
    if ic is not None:
        ic.save(STAGE / "icon.png"); print("icon.png ok")
    raw = STAGE / "thumb_raw.png"
    if raw.exists():
        im = Image.open(raw).convert("RGB")
        w, h = im.size
        tw, th = 800, 600
        s = max(tw / w, th / h); im = im.resize((int(w * s) + 1, int(h * s) + 1), Image.Resampling.LANCZOS)
        im = im.crop(((im.width - tw) // 2, (im.height - th) // 2, (im.width - tw) // 2 + tw, (im.height - th) // 2 + th)).convert("RGBA")
        d = ImageDraw.Draw(im)
        def font(sz):
            for c in (r"C:\Windows\Fonts\seguisb.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
                try: return ImageFont.truetype(c, sz)
                except Exception: pass
            return ImageFont.load_default()
        for txt, y, sz, col in (("REACTIVE CRAFTING", 28, 70, (245, 230, 200, 255)), ("Terrain-altering throwables", 112, 30, (224, 178, 94, 255))):
            f = font(sz); bb = d.textbbox((0, 0), txt, font=f); x = (tw - (bb[2] - bb[0])) / 2
            d.text((x + 2, y + 2), txt, font=f, fill=(0, 0, 0, 220)); d.text((x, y), txt, font=f, fill=col)
        im.save(STAGE / "thumbnail2.png"); print("thumbnail2.png ok")
    # contact sheet (x6) for review
    parts = [("abilities", ab), ("passives", ps), ("items", it), ("glyphs", gl)]
    W = max(p[1].width for p in parts) * 6; H = sum(p[1].height * 6 + 10 for p in parts)
    cs = Image.new("RGBA", (W, H), (46, 42, 52, 255)); y = 0
    for n, p in parts:
        u = p.resize((p.width * 6, p.height * 6), Image.Resampling.NEAREST); cs.paste(u, (0, y), u); y += u.height + 10
    cs.save(STAGE / "contact_sheet.png"); print("contact_sheet.png written")
