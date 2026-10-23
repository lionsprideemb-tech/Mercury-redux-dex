# Mercury Redux sprite roster — non-destructive integration handoff (2026-10-23)

## Authority
The active sprite/artist/identity review remains exclusively in [Sprites/master-review.html](https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review.html), published on [GitHub Pages](https://lionsprideemb-tech.github.io/Sprites/master-review.html). Its source data is [Sprites/master-review-data.json](https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json). Do not create an independent second approval state in the Pokédex app.

## User decisions
The latest submitted iPhone export, [review/user-iphone-decisions-2026-10-23.json](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/user-iphone-decisions-2026-10-23.json), contains **166 explicit user choices (154 KEEP, 12 CUT)**. KEEP/CUT describes that exact candidate artwork, not necessarily a safe species ID, evolution relationship, or complete sprite package. Preserve earlier historical GBA/DS decisions and the export even when an asset needs repair. Current canonical reviewer reports 156 active cards (the original 154 plus 2 current-pass Wailmer/Wailord reviews), 16 held cards, and 25 identity/name/family warnings (overlapping categories; not final Pokédex totals).

## Artist/name guardrail
A source filename, author credit, artist pack, or regional-form label must **never** be promoted to a new Pokémon species by itself. Some old source pages emitted **Mikitarian** and **Luminian** as names even when these represented regional/source designations. Keep separate evidence fields for original source label, correct Pokémon or base species, form name, credited artist, family and source URL. Identity conflicts are in [the identity audit](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-provenance-audit-2026-10-23.json) and must be verified before Dex placement.

## Sprite-integrity gate
Do not infer valid front/back pairing from adjacent numbered embedded images. [Platinum Redux workbook mapping summary](https://github.com/lionsprideemb-tech/Sprites/blob/main/DS_CUSTOM_LIBRARY/DS_READY_MASTER/platinum_redux_workbook_map_summary.json) recorded only **3 species-matched authoritative entries out of 212**; these unresolved bindings need source-level verification. Never overwrite an approved sprite, assign a new national species number, alter evolution families, or propagate an unverified type automatically.

## Scope of this commit
Documentation only. The Dex data, roster entries, user votes, and game files are unchanged. All creative decisions must continue in the canonical Sprites reviewer; export/import user choices explicitly into versioned GitHub records.

## October 23 follow-up — source preview recovery
The original front/back/shiny GBA assets for Flying-type alternate Wailmer and Wailord were recovered in the Sprites repository and exposed as two still-undecided creative comparisons. The preserved **166 explicit iPhone votes remain unchanged**. Those two source designs have **not** been certified as DS-ready, assigned Pokédex IDs, or integrated into Platinum. The canonical reviewer now opens on outstanding families and its bulk KEEP action is restricted to designs actually visible on the current page.


## Major reviewer and evidence-triage update — October 23, 2026
The sole creative review interface remains [Sprites/master-review.html](https://lionsprideemb-tech.github.io/Sprites/master-review.html). It now includes a **read-only Approved source art** mode: all **74 historically approved original GBA-source front/back pairs**, grouped into **39 actual families**, with original labels, real recorded types, front/back and shiny views. Missing-shiny filtering isolates exactly **five** alternate forms (Breloom, Combee, Vespiquen, Dwebble and Crustle). They require original-source recovery and are **not** candidates for a second KEEP vote.

- [Five missing shiny source repairs](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/legacy-approved-artwork-repair-2026-10-23.json)
- [Grouped identity/family source conflicts](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-family-triage-2026-10-23.json): 19 held source records (10 evolution evidence conflicts, 6 ambiguous artist/region labels, 3 unverified labels). No guessed family or Pokémon ID is promoted to canon.
- [Regression source checks](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/tests/master-review-integrity.cjs) and [GitHub Actions workflow](https://github.com/lionsprideemb-tech/Sprites/blob/main/.github/workflows/sprite-review-integrity.yml).

The **166 original iPhone decisions (154 KEEP / 12 CUT)** are untouched. Backup imports now **merge** rather than discard absent votes, preserve non-current identifiers, and save unresolved technical-hold identity corrections. A GitHub JSON export is still required before review choices become committed project state; the Pages reviewer does not push to GitHub itself.

**Safety:** This was a reviewer, metadata, and test update. The 74 sources remain **GBA originals, not certified DS sprite conversions**. There have been no edits to the ROM, gameplay, Pokédex species registry, stored historical votes, or artwork files. Do not infer a checked GitHub Actions run from the existence of the workflow alone.
