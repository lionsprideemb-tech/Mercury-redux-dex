# Mercury Redux sprite roster — non-destructive integration handoff (2026-10-23)

## Authority
The active sprite/artist/identity review remains exclusively in [Sprites/master-review.html](https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review.html), published on [GitHub Pages](https://lionsprideemb-tech.github.io/Sprites/master-review.html). Its source data is [Sprites/master-review-data.json](https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json). Do not create an independent second approval state in the Pokédex app.

## User decisions
The latest submitted iPhone export, [review/user-iphone-decisions-2026-10-23.json](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/user-iphone-decisions-2026-10-23.json), contains **166 explicit user choices (154 KEEP, 12 CUT)**. KEEP/CUT describes that exact candidate artwork, not necessarily a safe species ID, evolution relationship, or complete sprite package. Preserve earlier historical GBA/DS decisions and the export even when an asset needs repair. Current canonical reviewer reports 154 active cards, 18 held cards, and 25 identity/name/family warnings (overlapping categories; not final Pokédex totals).

## Artist/name guardrail
A source filename, author credit, artist pack, or regional-form label must **never** be promoted to a new Pokémon species by itself. Some old source pages emitted **Mikitarian** and **Luminian** as names even when these represented regional/source designations. Keep separate evidence fields for original source label, correct Pokémon or base species, form name, credited artist, family and source URL. Identity conflicts are in [the identity audit](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-provenance-audit-2026-10-23.json) and must be verified before Dex placement.

## Sprite-integrity gate
Do not infer valid front/back pairing from adjacent numbered embedded images. [Platinum Redux workbook mapping summary](https://github.com/lionsprideemb-tech/Sprites/blob/main/DS_CUSTOM_LIBRARY/DS_READY_MASTER/platinum_redux_workbook_map_summary.json) recorded only **3 species-matched authoritative entries out of 212**; these unresolved bindings need source-level verification. Never overwrite an approved sprite, assign a new national species number, alter evolution families, or propagate an unverified type automatically.

## Scope of this commit
Documentation only. The Dex data, roster entries, user votes, and game files are unchanged. All creative decisions must continue in the canonical Sprites reviewer; export/import user choices explicitly into versioned GitHub records.
