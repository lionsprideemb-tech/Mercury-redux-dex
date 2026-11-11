#!/usr/bin/env python3
"""Read-only Mercury Redux Delta Flygon architecture audit.

Run from the Mercury-redux-dex repository root, with sparse checkouts of
Sprites, platinum-modern-ds and pinned upstream pokeplatinum. Writes reports
only to the given output directory. It does not modify a Pokédex or ROM.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

FAMILY = ("trapinch", "vibrava", "flygon")
WATCH_NUMBERS = (1581, 1751, 1761, 2081, 2082)
WATCH_REVIEWS = ("R0494", "R0496")
FIELDS = ("key", "id", "reviewId", "displayName", "name", "basePokemon",
          "sourceConstant", "publicConstant", "constant", "nationalDex",
          "types", "evolutions", "integrationState", "classification",
          "rosterGroup", "form", "formId")

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_b64_gzip_json(path: Path):
    raw = base64.b64decode("".join(path.read_text().split()))
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)

def limited_record(p: dict) -> dict:
    return {k: p[k] for k in FIELDS if k in p}

def load_effective_dex(root: Path):
    index = json.loads((root / "data/pokedex/index.json").read_text())
    shards = index.get("shards", [])
    overlays = index.get("overlays", [])
    data = []
    for filename in shards:
        data.extend(load_b64_gzip_json(root / "data/pokedex" / filename).get("pokemon", []))
    base_count = len(data)
    for filename in overlays:
        overlay = load_b64_gzip_json(root / "data/pokedex" / filename)
        by_key = {p.get("key"): p for p in data}
        for patch in overlay.get("patches", []):
            row = by_key.get(patch.get("key"))
            if row is not None:
                row.update(patch.get("set") or {})
        for item in overlay.get("additions", []):
            k = item.get("key")
            if not k or k in by_key:
                continue
            row = dict(item)
            row.update(row.pop("set", {}) or {})
            data.append(row)
            by_key[k] = row
        removed = set(overlay.get("removeKeys", []))
        data = [p for p in data if p.get("key") not in removed]
    return index, data, base_count

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--sprites", type=Path, required=True)
    cli.add_argument("--platinum", type=Path, required=True)
    cli.add_argument("--upstream", type=Path, required=True)
    cli.add_argument("--donor", type=Path, required=True)
    cli.add_argument("--output", type=Path, default=Path("qa-delta-output"))
    a = cli.parse_args()

    index, rows, base_count = load_effective_dex(Path("."))
    hits = []
    by_id = defaultdict(list)
    by_key = defaultdict(list)
    for p in rows:
        search = " ".join(str(p.get(k, "")) for k in
            ("key", "displayName", "name", "basePokemon", "sourceConstant",
             "publicConstant", "constant", "reviewId")).lower()
        if any(x in search for x in FAMILY) or str(p.get("reviewId", "")).upper() in WATCH_REVIEWS:
            hits.append(limited_record(p))
        if isinstance(p.get("id"), int):
            by_id[p["id"]].append(p)
        if p.get("key"):
            by_key[p["key"]].append(p)

    duplicates = [{
        "id": number, "records": [limited_record(p) for p in recs]
    } for number, recs in sorted(by_id.items()) if len(recs) > 1]
    duplicate_keys = [{
        "key": key, "records": [limited_record(p) for p in recs]
    } for key, recs in by_key.items() if len(recs) > 1]
    watched = [{
        "id": number, "records": [limited_record(p) for p in by_id.get(number, [])]
    } for number in WATCH_NUMBERS]

    votes_path = a.sprites / "review/user-iphone-decisions-2026-10-23.json"
    votes = json.loads(votes_path.read_text())
    plan_path = a.sprites / "review/flygon-roster-plan-2026-11-09.json"
    plan = json.loads(plan_path.read_text())
    registry_path = a.platinum / "data/canonical_species_1025.txt"
    registry = [line.strip() for line in registry_path.read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
    icon_c_path = a.upstream / "src/pokemon_icon.c"
    icon_c = icon_c_path.read_text()
    pokemon_h_path = a.upstream / "include/struct_defs/pokemon.h"
    pokemon_h = pokemon_h_path.read_text()
    donor_path = a.donor / "data/IconPaletteTable.c"
    donor_text = donor_path.read_text()
    pairs = [(key, int(v)) for key, v in re.findall(
        r"^\s*\[\s*(SPECIES_[A-Z0-9_]+|\d+)\s*\]\s*=\s*(\d+)\s*,",
        donor_text, re.M)]
    palette_counts = dict(sorted(Counter(v for _, v in pairs).items()))
    base_palette = [(k, v) for k, v in pairs if k.startswith("SPECIES_")]
    native_form_routing = re.search(
        r"u16 BoxPokemon_IconFormOffset\(.*?\n\}", icon_c, re.S)
    form_routes = re.findall(
        r"case (SPECIES_[A-Z0-9_]+):", native_form_routing.group(0)
    ) if native_form_routing else []

    result = {
        "schema": "mercury-delta-flygon-architecture-audit-v1",
        "mode": "READ_ONLY__NO_GAME_OR_DEX_EDITS",
        "dex": {
            "index_sha256": digest(Path("data/pokedex/index.json")),
            "shards": len(index.get("shards", [])),
            "overlays": len(index.get("overlays", [])),
            "base_rows_before_overlays": base_count,
            "effective_rows": len(rows),
            "declared_rows": index.get("meta", {}).get("entries"),
            "effective_matches_declared": len(rows) == index.get("meta", {}).get("entries"),
            "flygon_family_related_records": hits,
            "duplicate_numeric_site_ids": duplicates,
            "duplicate_keys": duplicate_keys,
            "watched_site_ids": watched,
            "site_id_is_not_platinum_species_id": True
        },
        "sprites": {
            "historical_ledger_sha256": digest(votes_path),
            "historical_votes": votes.get("count"),
            "historical_keep": votes.get("keepCount"),
            "historical_cut": votes.get("cutCount"),
            "vote_entries_count": len(votes.get("entries", [])),
            "roster_plan_sha256": digest(plan_path),
            "planned_delta_count": plan.get("plannedStructure", {}).get("deltaFamily", {}).get("newSpeciesOrFormSlots"),
            "retired_roster_identities": [x.get("identity") for x in plan.get("excludedFromPlannedRoster", [])]
        },
        "platinum": {
            "registry_sha256": digest(registry_path),
            "canonical_registry_count": len(registry),
            "unique_canonical_names": len(set(registry)),
            "tail": registry[-3:],
            "delta_species_constants_present": [x for x in registry
                if any(f"DELTA_{fam.upper()}" in x for fam in FAMILY)],
            "species_u16_not_free_id_proof": True,
            "pinned_icon_source_sha256": digest(icon_c_path),
            "pinned_icon_form_routes": sorted(set(form_routes)),
            "pinned_icon_form_route_has_flygon_family": any(
                any(fam.upper() in name for fam in FAMILY) for name in form_routes),
            "pinned_pokemon_form_five_bits": "u8 form : 5;" in pokemon_h,
            "icon_source_uses_palette_lookup": "sPokemonIconPaletteIndex[species]" in icon_c,
            "icon_source_fallback_unknown_form": "return IconTilesIndex(species);" in icon_c,
            "donor_palette_source_sha256": digest(donor_path),
            "donor_explicit_palette_assignments": len(pairs),
            "donor_palette_assignments_by_bank": palette_counts,
            "donor_species_only_explicit_assignments": len(base_palette),
            "donor_species_palette_counts": dict(sorted(Counter(v for _,v in base_palette).items())),
            "bank3_no_donor_assignments": 3 not in palette_counts,
            "bank3_runtime_ui_safe": "UNPROVEN"
        },
        "notes": [
            "Dex row id/reviewId, even when numeric, does NOT allocate a native DS species ID.",
            "Retired source-art KEEP votes must remain distinct from current playable roster exclusions.",
            "Absence of donor bank-3 assignments is not proof that all menu/VRAM contexts load or preserve a fourth shared icon palette.",
            "This audit does not allocate IDs, alter Dex overlays, approve sprites or certify emulator behavior."
        ]
    }
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / "audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    summary = [
        "# Delta Flygon QA — computed read-only audit",
        "",
        f"- Effective Dex: **{len(rows)}** rows from {len(index.get('shards', []))} shards / {len(index.get('overlays', []))} overlays; declared {index.get('meta', {}).get('entries')}.",
        f"- Historical sprite votes: **{votes.get('count')}** ({votes.get('keepCount')} KEEP, {votes.get('cutCount')} CUT); read only.",
        f"- Native canonical registry: **{len(registry)}** entries, **{len(set(registry))}** distinct; custom Delta constants: {result['platinum']['delta_species_constants_present']}.",
        f"- Active site-ID duplicates: **{len(duplicates)}** distinct numbers; active key duplicates: **{len(duplicate_keys)}**.",
        f"- Delta-family matching live Dex records: **{len(hits)}** (see JSON for exact identities).",
        f"- Pinned icon form routing specifically handles the Flygon family: **{result['platinum']['pinned_icon_form_route_has_flygon_family']}**.",
        f"- Donor palette assignments by bank: **{palette_counts}**; bank-3 runtime safety **UNPROVEN**.",
        "",
        "## Stop gates",
        "1. Do not identify Dex site IDs as native Platinum IDs or reuse IDs from duplicated site records.",
        "2. Resolve or explicitly exclude retired Redux B identities from future export without erasing historical votes.",
        "3. Verify icon lookup, bank 3 in each party/PC/trade/battle/UI path, all sprite archives and the 5-bit form representation.",
        "4. Validate stage-specific Bug typings and choose Delta evolution methods only after owner design signoff.",
        "5. Only after permissions, artwork approval and 4bpp/runtime tests: propose collision-safe IDs in a separate implementation PR.",
        "",
        "## Data files",
        "- audit.json contains all matching active entries, exact duplicate IDs and preserved checksums.",
        "- This report is from source-side static QA, not a playable ROM test.",
    ]
    (a.output / "README.md").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))

if __name__ == "__main__":
    main()
