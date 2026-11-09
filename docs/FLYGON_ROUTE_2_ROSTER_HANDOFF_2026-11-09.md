# Mercury Pokédex — Flygon Route 2 roster handoff (2026-11-09)

The user's latest explicit roster selection is **normal Trapinch → Vibrava → Flygon and exactly one regular Mega Flygon, plus a separate future Delta Trapinch → Delta Vibrava → Delta Flygon line with a Bug/Ground Delta Flygon**. The Electric/Dragon-themed Redux B Flygon and its Redux B Mega are **removed from the proposed game roster**. No Delta Mega is planned.

Canonical planning source: [Sprites/review/flygon-roster-plan-2026-11-09.json](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/flygon-roster-plan-2026-11-09.json) and [human-readable decision](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/FLYGON_ROUTE_2_DECISION_2026-11-09.md).

**Integration rules**
- Keep ordinary Flygon evolution and canonical typing unchanged.
- Keep one regular Flygon Mega slot; older archived approvals for multiple competing Mega artworks are not approval for multiple separate Mega identities. The previously approved Elite Redux `flygon-mega` is the baseline candidate pending full native graphics/runtime validation.
- Plan just three additional Delta species/form entries, **not yet instantiated**. Delta Flygon's target types are Bug/Ground. Early-stage Delta types and all three source-specific art selections remain unresolved; do not invent them.
- Do not import `flygon-redux-b` or `flygon-redux-b-mega` into the Dex/ROM, despite their old art KEEP votes. Both source sprite folders remain preserved and their votes remain historical truth.
- The generic `ER125_REDUX_TO_DELTA_MAP.csv` rows for `SPECIES_FLYGON_REDUX`, `SPECIES_FLYGON_REDUX_MEGA`, `SPECIES_TRAPINCH_REDUX`, and `SPECIES_VIBRAVA_REDUX` are **superseded for this family**. Do not promote previously rejected `flygon-redux`, `flygon-redux-mega`, `trapinch-redux` or undecided `vibrava-redux` as Bug/Ground art.
- New Delta stage allocation, evolution routing, sprite icons, 4bpp palette and ROM work require separate quality/collision/build checks.

This handoff intentionally changes **no Pokédex records, species IDs, evolution methods, encounter tables or production sprite assets**. It is a locked roster direction for a later implementation.
