# Mercury Redux — Delta Flygon collision-safe implementation proposal
**Date:** 2026-11-11  
**Status:** READ-ONLY QA / architecture recommendation; NOT APPROVED FOR ROM INTEGRATION  
**Evidence:** [machine-readable audit](DELTA_FLYGON_ARCHITECTURE_EVIDENCE_2026-11-11.json) · [successful pinned-source GitHub Actions run](https://github.com/lionsprideemb-tech/Mercury-redux-dex/actions/runs/43103979480)

## Scope and verified GitHub baselines

This QA branch was created from `Mercury-redux-dex/main` at `faa7cb4016d8030fb4661b49114352d79cac7944`. It checks the untouched source snapshots:
- Sprites: `f15c4671bf7afb15450fc7801bde17aefcdc4f7e`.
- Mercury-redux-dex: `faa7cb4016d8030fb4661b49114352d79cac7944`.
- platinum-modern-ds: `5525e961a1fb98c62bd53bc4a27b0276a39f6719`.
- Pinned pret/pokeplatinum: `c248fb3f8cc9934ded800e489567c5c0eeee92eb`.
- Pinned BluRosie/hg-engine: `5157c501dc0e6f88ef1654ab121352a5cc9ed7de`.

All three project main branches are unchanged by this work. No Pokédex overlay, sprite, historic approval, native species registry, engine source, or ROM binary was modified.

## Findings from the actual data

| Check | Verified finding | Interpretation |
|---|---|---|
| Dex data | 17 compressed shards + 12 overlays: 1,603 base rows to **1,599** live rows | Site records are not a DS species allocation table |
| History | **166** votes, including 154 KEEP and 12 CUT | Preserved exactly; no new artwork approval |
| Native DS registry | **1,025** distinct canonical species; no Delta Trapinch/Vibrava/Flygon constants | No Delta species ID has been assigned |
| Dex identity | **0** duplicate `key` values; **3** duplicated numeric `id` values | Numeric site IDs cannot be treated as unique species IDs |
| Icon code | Form-icon handling special-cases Unown, Deoxys, Burmy, Wormadam, Shellos, Gastrodon, Giratina, Shaymin and Rotom | No Delta Flygon-family form-icon route exists in pinned implementation |
| Form storage | Persistent `u8 form : 5` | A single alternate form fits, but form-aware gameplay is NOT automatic |
| Donor icon palette assignments | 1,535 explicit assignments: bank 0 = 844; bank 1 = 310; bank 2 = 381; bank 3 = 0 | Bank 3 is unused **in this donor table only**; no in-game palette safety claim |

### Exact duplicated site numeric IDs
These are duplicate **Dex display/source IDs**, NOT proved native-game collisions:
- `1581`: `R0077`, `R0078` — Arcanine Mega, same constant.
- `1751`: `R0901`, `R0902` — Toxtricity Mega, same constant.
- `1761`: `R0737`, `R0738` — Reuniclus Mega, same constant.

No duplicate `key` values were found. Preserve each historical row until the wider Dex identity policy establishes whether paired rows should remain separate source variants or be grouped under one implementation identity.

### Flygon rows: legacy site state versus newer game decision

Canonical `SPECIES_TRAPINCH` (#328), `SPECIES_VIBRAVA` (#329), and `SPECIES_FLYGON` (#330) remain present. The displayed ordinary evolution sequence is Trapinch `EVO_LEVEL 35` → Vibrava `EVO_LEVEL 45` → Flygon.

Additional existing *site* records include:
- `R0489` Trapinch Redux / ID 1816, `R0491` Vibrava Redux / ID 1817, `R0493` Flygon Redux / ID 1638 (Ice/Bug source route).
- `R0494` Flygon Redux B / ID **2081**, Electric/Dragon, and `R0496` Flygon Redux B Mega / ID **2082**, Electric/Dragon.
- `R0495` Flygon Mega / ID 1692; `R0497` Flygon Redux Mega / ID 1632; `R0498` Platinum Redux Flygon / ID 1888.

The two Redux B records **still appear in the reconstructed live Dex** and are labelled `SOURCE_BOUND`. This is a real *presentation/roster export-policy discrepancy* with the [newer Sprites Route 2 decision](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/FLYGON_ROUTE_2_DECISION_2026-11-09.md), which expressly **retires those two designs from the proposed playable roster**. Do not confuse their presence in a legacy reference site with current player approval, and do not delete their original artwork or votes. A future Dex export should carry a non-destructive exclusion/reconciliation policy in a separate, reviewed change.

The old Ice/Bug Redux line and alternate Mega variants are also *not* approved for automatic substitution as the new Orpheus-style Delta family. The [original Orpheus source review](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/ORPHEUS_THRACEAN_FLYGON_SOURCE_REVIEW_2026-11-09.md) notes unsafe evolution source metadata (Trapinch directly to Flygon, and Vibrava to Lycanroc). **Do not import those edges.** No exact Delta evolution levels have been approved.

## Architecture alternatives

| Decision factor | Three distinct custom Delta species | Three alternate forms of base species |
|---|---|---|
| Preserve vanilla Trapinch/Vibrava/Flygon stats and forms | Yes, with independent records | Yes, if all form lookups are correctly isolated |
| Three-stage Delta-only evolution | Native species-target edges *after* new IDs and data are registered | Needs form-specific evolution dispatch and target form preservation |
| Save/party storage | `u16 species` accommodates new IDs, but registry bounds/sentinels and save compatibility must be revised | Existing form field can encode one variant; all form consumers still need validation |
| Icons and palettes | Requires explicit custom species icon archive routing and verified shared-palette handling | Requires adding Flygon family to hard-coded form icon routing and palette handling |
| Pokédex / PC / trade | Requires defined custom species-to-Dex mapping and runtime tests | May share species caught state; distinct Delta identity requires explicit UI and capture-state policy |
| Collision risk | New *dedicated* custom namespace required; must not reuse 1026/1027 or site IDs | Form IDs are scoped per species, but form combinations and helpers can silently fallback to vanilla |
| Regression risk | Registry/sentinel work is significant, but variant evolution and identity are less ambiguous | Smaller number of species constants, but cross-cutting form/evolution/icon special cases and potential silent base-form fallback |

### Recommended architecture

**Prefer three distinct custom Delta species, on a future isolated engine implementation branch, under an explicit custom-species namespace.** This best honors an independently evolved Bug-themed three-stage family and avoids hiding the Delta progression behind the pinned engine's incomplete form handling.

This is a direction, **not permission to append numeric IDs now**. The current sealed native registry explicitly reserves **1–1025** for canonical species and **1026–1027** for Egg and Bad Egg. Neither `2081`/`2082` nor `1581`/`1751`/`1761`, nor a guessed `1028–1030`, is an approved Delta allocation. A future registry design must specify:
1. How custom IDs coexist with canonical 1–1025 and Egg/Bad Egg sentinels.
2. How `MAX_SPECIES`, `NATIONAL_DEX_COUNT`, icon bounds, archives, serialization and save migration accommodate the new namespace.
3. How independent Delta identity maps to National Dex UI, seen/caught flags, party, PC, trades and evolutions without modifying vanilla family behavior.
4. Whether this architecture scales to the larger approved Mercury custom roster rather than being a one-off Flygon hack.

Use provisional **symbolic labels only** during planning (`CUSTOM_DELTA_TRAPINCH`, `CUSTOM_DELTA_VIBRAVA`, `CUSTOM_DELTA_FLYGON`); these labels are *not* registered constants or assigned numeric IDs.

## Required implementation blockers, ordered

1. **Species namespace and save-state compatibility.** Approve a versioned custom ID/registry strategy and collision checker, then test save/PC/trade handling. Do not modify existing sealed canonical IDs or use arbitrary gaps.
2. **Icon routing and palette bank 3.** The empty donor bank 3 is no guarantee. Verify generated `pl_poke_icon.narc`, shared `NCLR` contents, indexed 4bpp icon pixels, palette slot addressing and lifetime in **party, PC, battle, summary, Pokédex, evolution, trade and storage UI**. Add explicit routing for new identities. Do not activate bank 3 blindly.
3. **Correct Delta evolution metadata.** Preserve canonical 35/45 progression. Define Delta Trapinch → Delta Vibrava → Delta Flygon with method/level choices explicitly approved later; reject the two erroneous Orpheus source edges.
4. **Source/art provenance.** Preserve original Orpheus silhouettes; stage-specific palettes and Bug on the two early stages, Bug/Ground on final Flygon. User-reported permission is not a verified public redistribution license. Artwork, icon and shiny sets are still **unapproved**.
5. **End-to-end graphics test.** Passing raw 64×64, 4bpp QA alone does not certify Nitro archive layout, paletted icons, sprite animations, DS screens or emulator behavior. Require four views + icon/shiny where mandated, native build, battle/party/PC/Pokédex/save-reload proof.
6. **Legacy site reconciliation.** Apply the newer Flygon Route 2 exclusion only in a future reviewed export policy. Preserve both retired Redux B records and all votes in the historic source ledger.

## Verification and boundaries

- [Read-only QA workflow](../.github/workflows/delta-flygon-architecture-qa.yml) checks pinned real source files; [machine report](DELTA_FLYGON_ARCHITECTURE_EVIDENCE_2026-11-11.json) preserves full IDs, SHA-256 hashes and source record values.
- [Successful read-only audit](https://github.com/lionsprideemb-tech/Mercury-redux-dex/actions/runs/43103979480) is static analysis, **not** a DS build or emulator pass.
- Preserve the historic **166 votes**, all source-art files, current design approvals, normal canonical family, one regular Mega plan, Dex main and platinum-modern-ds main.
- **No current ROM integration, no new species/form allocation, no artwork approval, no changes to native Platinum.**

**Next major release gate:** approve an architecture *plan only*, then implement a general custom-species registry and runtime-routing proof in a new isolated Platinum branch—never silently promote this QA documentation into the playable game.
