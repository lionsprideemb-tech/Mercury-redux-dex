#!/usr/bin/env python3
import base64, copy, csv, gzip, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEX = ROOT / "data" / "pokedex"
INDEX = DEX / "index.json"
R7 = DEX / "review_overlay_r7.json.gz.b64"
OUT = DEX / "completion_overlay_r8.json.gz.b64"
REPORT = DEX / "reports" / "open_118_completion_r8.tsv"
CHECKPOINT = ROOT / "R8_118_COMPLETION_CHECKPOINT.md"


def load_b64(path):
    raw = base64.b64decode(path.read_text().strip())
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def apply_overlay(rows, overlay):
    data = [dict(x) for x in rows]
    by_key = {x.get("key"): x for x in data if x.get("key")}
    for patch in overlay.get("patches", []):
        cur = by_key.get(patch.get("key"))
        if cur is not None:
            cur.update(patch.get("set") or {})
    for add in overlay.get("additions", []):
        key = add.get("key")
        if key and key not in by_key:
            cur = dict(add)
            cur.update(cur.pop("set", {}) or {})
            data.append(cur)
            by_key[key] = cur
    removed = set(overlay.get("removeKeys", []))
    return [x for x in data if x.get("key") not in removed]


def merged_rows(index):
    rows = []
    for shard in index.get("shards", []):
        rows.extend(load_b64(DEX / shard).get("pokemon", []))
    for name in index.get("overlays") or ([index["overlay"]] if index.get("overlay") else []):
        if name == OUT.name:
            continue
        rows = apply_overlay(rows, load_b64(DEX / name))
    return rows


def stat_bst(stats):
    return sum(int(stats[k]) for k in ("hp", "atk", "def", "spa", "spd", "spe"))


def move_constant(name):
    if name.startswith("MOVE_"):
        return name
    return "MOVE_" + re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")


def level_number(value):
    try:
        return int(value)
    except Exception:
        return 999


# Draft-only labels that are not implemented in the current Mercury source.
ABILITY_SUBS = {"Airborne": "Levitate", "Fossilized": "Battle Armor"}

# Official Mega spreads for approved alternate-Mega visuals that R7 accidentally
# inherited from the normal species. Typing/abilities remain Mercury alternate values.
MEGA_STATS = {
    "R0022": {"hp": 83, "atk": 80, "def": 80, "spa": 135, "spd": 80, "spe": 121},
    "R0299": {"hp": 90, "atk": 95, "def": 105, "spa": 165, "spd": 110, "spe": 45},
    "R0450": {"hp": 50, "atk": 85, "def": 125, "spa": 85, "spd": 115, "spe": 20},
    "R0464": {"hp": 70, "atk": 75, "def": 80, "spa": 135, "spd": 80, "spe": 135},
    "R0505": {"hp": 75, "atk": 110, "def": 110, "spa": 110, "spd": 105, "spe": 80},
    "R0556": {"hp": 95, "atk": 145, "def": 130, "spa": 120, "spd": 90, "spe": 120},
    "R0561": {"hp": 80, "atk": 145, "def": 150, "spa": 105, "spd": 110, "spe": 110},
}

# Later project sprite authorities supersede generic Original-Megas provenance.
STAGE_SPRITES = {
    "R0175": ("STAGE22_CUSTOM_MASTER", "Mega Rhyperior Saturn siege-artillery visual authority"),
    "R0205": ("STAGE23_GRAPHICS_COMPLETE", "Mega Electivire graphics package"),
    "R0210": ("STAGE21_TECHNICAL_CANDIDATE", "Mega Magmortar technical sprite candidate"),
    "R0310": ("STAGE20_R4_MASTER", "Mega Yanmega R4 graphics authority"),
    "R0315": ("STAGE7_LOCKED_MASTER", "Mega Honchkrow approved visual package"),
    "R0343": ("STAGE14_XY_LOCK", "Mega Weavile converted X/Y master lineage"),
    "R0354": ("STAGE10R3_LOCKED_MASTER", "Mega Mamoswine glacier-armored GBA master"),
    "R0517": ("LOCKED_PRE_STAGE23_MASTER", "Cynthia Mega Milotic approved four-view art"),
    "R0602": ("STAGE9_LOCKED_MASTER", "Mega Bastiodon GBA-ready visual package"),
    "R0628": ("STAGE12R1_LOCKED_MASTER", "Mega Purugly owner-approved visual package"),
    "R0631": ("STAGE13R2_LOCKED_MASTER", "Mega Skuntank clean toxic-exhaust visual package"),
    "R0633": ("STAGE11R1_LOCKED_MASTER", "Mega Bronzong owner-approved visual package"),
    "R0648": ("STAGE20_MASTER", "Mega Hippowdon dedicated graphics authority"),
    "R0652": ("STAGE16R1_LOCKED_MASTER", "Mega Drapion owner-approved visual lineage"),
}

POSTSEAL_SPRITES = {
    "PS0001": ("POSTSEAL_MASTER_REQUIRED", "Delta Tyrantrum approved visual identity"),
    "PS0002": ("POSTSEAL_MASTER_REQUIRED", "Mega Houndoom Z approved visual identity"),
}


def sprite_metadata(cur):
    key = cur["key"]
    source = cur.get("source") or ""
    if key in STAGE_SPRITES:
        status, note = STAGE_SPRITES[key]
        return {"spritePackageStatus": status, "spriteProvenance": source or "Mercury Redux Custom", "spriteBindingState": "MASTER_KNOWN__NEXTDEX_ATLAS_IMPORT_PENDING", "spriteNotes": note}
    if key in POSTSEAL_SPRITES:
        status, note = POSTSEAL_SPRITES[key]
        return {"spritePackageStatus": status, "spriteProvenance": source or "Mercury Redux Custom", "spriteBindingState": "APPROVED_VISUAL_IDENTITY__ATLAS_IMPORT_PENDING", "spriteNotes": note}
    if "Reborn" in source or "Plates" in source or "BlueTowel" in (cur.get("displayName") or ""):
        return {"spritePackageStatus": "STAGED_4_VIEW_IDENTITY_RESOLVED", "spriteProvenance": source, "spriteBindingState": "SOURCE_PACKAGE_BINDING_PENDING", "spriteNotes": "REV6 resolved the exact alternate-form visual identity and staged four-view preview; import the approved package into the NextDex atlas."}
    if "Banished Platinum" in source or "Original Megas" in source:
        return {"spritePackageStatus": "SOURCE_FRONT_BACK_RESOLVED", "spriteProvenance": source, "spriteBindingState": "GBA_CONVERSION_OR_ATLAS_BINDING_PENDING", "spriteNotes": "Original-Megas source identity is confirmed. Use a later Mercury master when listed; otherwise finish shiny/icon/palette/atlas work."}
    if "Elite Redux" in source:
        return {"spritePackageStatus": "ER_IDENTITY_RESOLVED", "spriteProvenance": source, "spriteBindingState": "SOURCE_IMPORT_OR_ATLAS_BINDING_PENDING", "spriteNotes": "Elite Redux source identity is resolved; bind the recovered art package to the Mercury atlas."}
    if "Mercury Redux Custom" in source:
        return {"spritePackageStatus": "MERCURY_CUSTOM_IDENTITY_RESOLVED", "spriteProvenance": source, "spriteBindingState": "CUSTOM_MASTER_ATLAS_BINDING_PENDING", "spriteNotes": "Preserve the approved project master art; atlas binding is separate from gameplay completion."}
    return {"spritePackageStatus": "IDENTITY_RESOLVED", "spriteProvenance": source, "spriteBindingState": "ATLAS_BINDING_PENDING", "spriteNotes": "Approved visual identity retained; atlas materialization remains."}


def main():
    index = json.loads(INDEX.read_text())
    rows = merged_rows(index)
    current_open = [x for x in rows if x.get("integrationState") == "APPROVED_DESIGN_RECORD"]
    assert len(current_open) == 118, f"Expected 118 open design records, found {len(current_open)}"

    by_const = {}
    for p in rows:
        for field in ("constant", "sourceConstant", "publicConstant"):
            if p.get(field):
                by_const[p[field]] = p

    ability_map = {}
    for p in rows:
        for field in ("primaryAbilities", "innates"):
            for item in p.get(field) or []:
                if isinstance(item, dict) and item.get("name"):
                    ability_map.setdefault(item["name"].lower(), copy.deepcopy(item))

    r7 = load_b64(R7)
    for name, definition in (r7.get("abilityDefinitions") or {}).items():
        ability_map[name.lower()] = copy.deepcopy(definition)
    r7_by = {x["key"]: x for x in r7.get("patches", []) + r7.get("additions", [])}

    def ability(name):
        name = ABILITY_SUBS.get(name, name)
        if name.lower() in ability_map:
            return copy.deepcopy(ability_map[name.lower()])
        const = "ABILITY_" + re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")
        return {"constant": const, "name": name, "description": "Existing Mercury/Redux ability; display description pending source sync."}

    patches = []
    report = []
    for cur in current_open:
        key = cur["key"]
        rr = r7_by[key]
        draft = rr.get("set") or {}
        inherit_const = rr.get("inheritFrom")
        base = by_const.get(inherit_const)
        assert base is not None, f"{key}: missing inheritFrom {inherit_const}"

        types = cur.get("types") or draft.get("types") or base.get("types") or []
        cstats = cur.get("stats") or {}
        current_stats_ok = all(cstats.get(x) is not None for x in ("hp", "atk", "def", "spa", "spd", "spe"))
        if current_stats_ok:
            stats = {x: int(cstats[x]) for x in ("hp", "atk", "def", "spa", "spd", "spe")}
            stat_source = "CURRENT_LOCKED_RECORD"
        elif draft.get("stats"):
            stats = {x: int(draft["stats"][x]) for x in ("hp", "atk", "def", "spa", "spd", "spe")}
            stat_source = "R7_RECOVERED_EXPLICIT"
        elif key in MEGA_STATS:
            stats = dict(MEGA_STATS[key])
            stat_source = "CANON_MEGA_SPREAD_FOR_ALTERNATE_MEGA"
        else:
            stats = {x: int(base["stats"][x]) for x in ("hp", "atk", "def", "spa", "spd", "spe")}
            stat_source = f"INHERITED_{inherit_const}"

        primary_names = [ABILITY_SUBS.get(x, x) for x in (draft.get("primaryAbilityNames") or [])]
        innate_names = [ABILITY_SUBS.get(x, x) for x in (draft.get("innateNames") or [])]
        primary = [ability(x) for x in primary_names]
        innates = [ability(x) for x in innate_names]

        moves = copy.deepcopy(base.get("levelUpMoves") or [])
        seen = {(str(x.get("level")), x.get("move")) for x in moves if isinstance(x, dict)}
        for extra in rr.get("extraMoves") or []:
            level = str(extra.get("level", "1"))
            move = move_constant(str(extra.get("move", "")))
            if (level, move) not in seen:
                moves.append({"level": level, "move": move, "source": "R8 type-aware addition"})
                seen.add((level, move))
        moves.sort(key=lambda x: (level_number(x.get("level")), x.get("move") or ""))

        owner_locked = bool(draft.get("primaryLocked")) or "Locked" in str(draft.get("designStatus", ""))
        sprite = sprite_metadata(cur)
        completed = {
            "types": types,
            "stats": stats,
            "bst": stat_bst(stats),
            "primaryAbilities": primary,
            "primaryAbilityNames": primary_names,
            "ability": primary[0] if len(primary) == 1 else None,
            "innates": innates,
            "innateNames": innate_names,
            "levelUpMoves": moves,
            "designStatus": "Locked / approved" if owner_locked else "Complete / adjustable",
            "reviewDraft": False,
            "mechanicsStatus": "OWNER_LOCKED_OR_POSTSEAL" if owner_locked else "R8_FILLED_DEFAULT",
            "completionPass": "R8_118_COMPLETION_2026-09-15",
            "statSource": stat_source,
            "learnsetSource": f"Inherited from {inherit_const} + R7 type-aware additions",
            "abilitySource": "Recovered owner-locked/post-seal package" if owner_locked else "Recovered R7 package; unimplemented draft labels replaced with existing Mercury abilities",
            "integrationState": "APPROVED_DESIGN_RECORD",
            **sprite,
        }
        patches.append({"key": key, "set": completed})
        report.append({
            "key": key, "name": cur.get("displayName") or cur.get("name"), "types": "/".join(types),
            "stats": "/".join(str(stats[x]) for x in ("hp", "atk", "def", "spa", "spd", "spe")),
            "bst": completed["bst"], "primary": ", ".join(primary_names), "innates": ", ".join(innate_names),
            "moves": len(moves), "stat_source": stat_source, "mechanics": completed["mechanicsStatus"],
            "sprite_package": sprite["spritePackageStatus"], "sprite_binding": sprite["spriteBindingState"],
        })

    overlay = {
        "version": "R8-118-COMPLETION-2026-09-15",
        "notes": "Completes gameplay-facing data for all 118 approved design records without falsely marking ROM/source integration complete. Restores R7 design packages, materializes inherited stats/learnsets, uses canonical Mega stats for alternate-Mega visual rows, replaces Airborne->Levitate and Fossilized->Battle Armor because those draft labels are not implemented, and records known sprite-package provenance separately from atlas binding.",
        "abilityDefinitions": r7.get("abilityDefinitions", {}),
        "patches": patches, "additions": [], "removeKeys": []
    }

    raw = json.dumps(overlay, separators=(",", ":"), ensure_ascii=False).encode()
    OUT.write_text(base64.b64encode(gzip.compress(raw, compresslevel=9)).decode() + "\n")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w", newline="") as f:
        fields = ["key", "name", "types", "stats", "bst", "primary", "innates", "moves", "stat_source", "mechanics", "sprite_package", "sprite_binding"]
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader(); writer.writerows(report)

    # Validate the completed overlay against the current merged dataset.
    validated = apply_overlay(rows, overlay)
    completed_rows = [x for x in validated if x.get("integrationState") == "APPROVED_DESIGN_RECORD"]
    assert len(completed_rows) == 118
    for p in completed_rows:
        assert len(p.get("types") or []) in (1, 2), (p.get("key"), "types")
        stats = p.get("stats") or {}
        assert all(stats.get(x) is not None for x in ("hp", "atk", "def", "spa", "spd", "spe")), (p.get("key"), "stats")
        assert p.get("bst") == stat_bst(stats), (p.get("key"), "bst")
        assert p.get("primaryAbilities") and p.get("innates") and p.get("levelUpMoves"), (p.get("key"), "gameplay")

    if OUT.name not in index.get("overlays", []):
        index.setdefault("overlays", []).append(OUT.name)
    meta = index.setdefault("meta", {})
    meta.update({
        "version": "Source-linked R8 — 118 design records completed",
        "generated": "2026-09-15",
        "approvedDesignRecords": 118,
        "sourceWorkOpenCount": 118,
        "completedDesignDataCount": 118,
        "completedDesignDataOverlay": OUT.name,
        "spriteIdentityResolvedForOpenRecords": 118,
        "spriteAtlasPendingForOpenRecords": 118,
        "policy": "Every row is approved. R8 completes gameplay/design data for the 118 source-work-open records; integrationState still describes ROM/source implementation, and spriteAtlas is not fabricated until the approved package is physically imported."
    })
    INDEX.write_text(json.dumps(index, separators=(",", ":"), ensure_ascii=False))

    stage_counts = {}
    for row in report:
        stage_counts[row["sprite_package"]] = stage_counts.get(row["sprite_package"], 0) + 1
    locked = sum(row["mechanics"] == "OWNER_LOCKED_OR_POSTSEAL" for row in report)
    CHECKPOINT.write_text(
        "# Pokémon Mercury Redux — R8 118-record completion checkpoint\n\n"
        "Date: 2026-09-15\n\n"
        "## Result\n"
        "- 118 / 118 approved design records now have complete typing, six stats/BST, Primary ability data, three Innates, and level-up learnsets.\n"
        f"- {locked} rows preserve explicit owner-locked/post-seal package flags; the other {118-locked} are filled defaults and remain editable by the owner.\n"
        "- Airborne was replaced with Levitate and Fossilized with Battle Armor because the two draft names are not implemented in the current source.\n"
        "- Alternate Mega rows that had inherited normal-form stats now use the corresponding official Mega stat spread while keeping their Mercury alternate typing/ability identity.\n"
        "- Source/ROM implementation remains open for these 118; this checkpoint does not falsely mark them source-bound.\n"
        "- Sprite identity/provenance is recorded for all 118. No fake spriteAtlas pointer is created; atlas import remains a physical asset task.\n\n"
        "## Files\n"
        "- `data/pokedex/completion_overlay_r8.json.gz.b64` — active R8 data overlay\n"
        "- `data/pokedex/reports/open_118_completion_r8.tsv` — human-reviewable 118-row report\n"
        "- `tools/build_r8_118_completion.py` — reproducible builder/validator\n"
    )

    print(f"R8 complete: {len(report)}/118 records validated")
    print(f"Owner-locked/post-seal flags: {locked}; filled defaults: {118-locked}")
    print("Sprite status counts:", stage_counts)


if __name__ == "__main__":
    main()
