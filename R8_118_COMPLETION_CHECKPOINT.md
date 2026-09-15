# Pokémon Mercury Redux — R8 118-record completion checkpoint

Date: 2026-09-15

## Result
- 118 / 118 approved design records now have complete typing, six stats/BST, Primary ability data, three Innates, and level-up learnsets.
- 7 rows preserve explicit owner-locked/post-seal package flags; the other 111 are filled defaults and remain editable by the owner.
- Airborne was replaced with Levitate and Fossilized with Battle Armor because the two draft names are not implemented in the current source.
- Alternate Mega rows that had inherited normal-form stats now use the corresponding official Mega stat spread while keeping their Mercury alternate typing/ability identity.
- Source/ROM implementation remains open for these 118; this checkpoint does not falsely mark them source-bound.
- Sprite identity/provenance is recorded for all 118. No fake spriteAtlas pointer is created; atlas import remains a physical asset task.

## Files
- `data/pokedex/completion_overlay_r8.json.gz.b64` — active R8 data overlay
- `data/pokedex/reports/open_118_completion_r8.tsv` — human-reviewable 118-row report
- `tools/build_r8_118_completion.py` — reproducible builder/validator
