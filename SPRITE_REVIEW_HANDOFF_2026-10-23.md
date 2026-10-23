# Pokémon Mercury Redux — Sprite curation handoff (2026-10-23)

This repository's Pokédex data and older mobile sprite-audit pages remain unchanged. The active **exception-only design approval** has moved to the dedicated Sprites repository:

- Master reviewer: https://lionsprideemb-tech.github.io/Sprites/master-review.html
- Live review data: https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json
- Protected historical decision ledger: https://github.com/lionsprideemb-tech/Sprites/blob/main/audit/2026-10-23/historical-decisions.json
- Technical/identity-repair queue: https://github.com/lionsprideemb-tech/Sprites/blob/main/audit/2026-10-23/repair-queue.json

## Recovery baseline

- 1,043 historical GBA approval rows retained (566 original KEEP and 477 original CUT).
- 94 later GBA decision rows reconciled, including 27 changed decisions.
- 246 purportedly new sprite imports were already rejected by the existing approval ledger; they are not offered again.
- 164 currently actionable candidate-art decisions; 35 technical holds (including two unextracted animation sheets).
- Fifteen genuine competing-art identities preserved, including options awaiting type/back verification.
- Five duplicate historical identity keys retained; two contain contradictory decisions (Hydreigon Mega and Tsareena Mega).

These counts describe overlapping curation ledgers and audits, **not** playable species totals. No Pokédex records, species IDs, evolution methods, type assignments or in-game sprites are altered by this handoff.

## Import gate

The reviewer autosaves locally and exports `mercury-sprite-decisions-v1` JSON and CSV. The user's exported decisions must be reconciled and committed in Sprites before treating them as approved for this Dex. Historical browser-only selections are not silently imported. Do not replace the existing Pokédex roster simply because a candidate appears in the review dataset.

The Sprites reviewer is authoritative for **candidate artwork selection**, not a direct ROM or Dex-integration authorization.
