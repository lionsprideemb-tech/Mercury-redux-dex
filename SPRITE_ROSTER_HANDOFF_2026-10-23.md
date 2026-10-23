# Mercury Redux — sprite roster handoff (2026-10-23)

## Source of truth
The canonical, iPhone-friendly, family-grouped review page is **Sprites/master-review.html**. Its data is **Sprites/master-review-data.json**. The sprite library keeps its historic sources unchanged.

- Canonical reviewer source: https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review.html
- Review data: https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json
- Uploaded iPhone choices: https://github.com/lionsprideemb-tech/Sprites/blob/main/review/user-iphone-decisions-2026-10-23.json
- Prior DS and polished CSV snapshots: https://github.com/lionsprideemb-tech/Sprites/blob/main/review/recovered-user-export-decisions-2026-10-23.json
- Artist/name/family attribution audit: https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-provenance-audit-2026-10-23.json

## Distinguish names and credits
The **source pack**, **credited artist**, **original filename/source label**, **actual Pokémon/form identity**, **types**, and **evolution family** are different fields. Never promote a label like "Mikitarian" or "Luminian" to a standalone Pokémon name solely because it appeared in an asset filename or creator catalog. Existing labels remain recoverable; suspect names and disputed family links go into the **Identity checks** view.

## Preservation
The previously uploaded user decision file contains **166 decisions: 154 KEEP and 12 CUT**. Of these, 154 match currently actionable cards; older/held entries must remain in exports. Original GBA and DS approval files stay intact. Do not re-ask approvals simply because a back sprite or metadata source is missing.

The 2026-10-23 canonical snapshot contains **156 active review entries (two additional unreviewed Wailmer/Wailord GBA previews), 16 technical holds, and 25 identity/name/family warnings** across active and held records; these counts are overlapping categories and are not final Pokédex species totals.

## Implementation gate
**No source sprites are deleted and no unapproved Pokémon, form, evolution link, or art source is integrated into the Platinum ROM.** A KEEP is an art/roster preference, not proof that a front/back/shiny/icon set is game-ready. Artist-name and family conflicts must be resolved before Pokédex placement and species ID assignment. Non-destructive technical repairs are performed separately.

## Validation
The existing sprite reviewer GitHub Actions integrity check passed at run https://github.com/lionsprideemb-tech/Sprites/actions/runs/40026325615 for the primary page and dataset. This is not a proof of a fully compiled ROM or an end-to-end iPhone Pages deployment.

**Dex rule:** Imported maker/region-like labels are not Pokédex names or species entries. Only the verified, user-approved manifest may be used to create/modify canonical display names, types, and evolutionary relationships.

## Subsequent verified approved-source linkage (2026-10-23)
A further **74 original Reborn / Plates alternate-form front/back pairs** have exact identity-based source-file links, with 69 complete four-view sets and **five missing shiny pairs** (Breloom, Combee, Vespiquen, Dwebble, Crustle alternate forms). This is **not a new approval queue**: all 74 had historical KEEP provenance. See [recovered approved legacy manifest](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/recovered-approved-legacy-pairs-2026-10-23.json) and [read-only reference gallery](https://lionsprideemb-tech.github.io/Sprites/approved-legacy-recovery.html). Source recovery is not DS conversion, icon validation or game integration. Latest Sprites integrity check for this batch: https://github.com/lionsprideemb-tech/Sprites/actions/runs/40031981811.


## Major reviewer and evidence-triage update — October 23, 2026
The sole creative review interface remains [Sprites/master-review.html](https://lionsprideemb-tech.github.io/Sprites/master-review.html). It now includes a **read-only Approved source art** mode: all **74 historically approved original GBA-source front/back pairs**, grouped into **39 actual families**, with original labels, real recorded types, front/back and shiny views. Missing-shiny filtering isolates exactly **five** alternate forms (Breloom, Combee, Vespiquen, Dwebble and Crustle). They require original-source recovery and are **not** candidates for a second KEEP vote.

- [Five missing shiny source repairs](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/legacy-approved-artwork-repair-2026-10-23.json)
- [Grouped identity/family source conflicts](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-family-triage-2026-10-23.json): 19 held source records (10 evolution evidence conflicts, 6 ambiguous artist/region labels, 3 unverified labels). No guessed family or Pokémon ID is promoted to canon.
- [Regression source checks](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/tests/master-review-integrity.cjs) and [GitHub Actions workflow](https://github.com/lionsprideemb-tech/Sprites/blob/main/.github/workflows/sprite-review-integrity.yml).

The **166 original iPhone decisions (154 KEEP / 12 CUT)** are untouched. Backup imports now **merge** rather than discard absent votes, preserve non-current identifiers, and save unresolved technical-hold identity corrections. A GitHub JSON export is still required before review choices become committed project state; the Pages reviewer does not push to GitHub itself.

**Safety:** This was a reviewer, metadata, and test update. The 74 sources remain **GBA originals, not certified DS sprite conversions**. There have been no edits to the ROM, gameplay, Pokédex species registry, stored historical votes, or artwork files. Do not infer a checked GitHub Actions run from the existence of the workflow alone.
