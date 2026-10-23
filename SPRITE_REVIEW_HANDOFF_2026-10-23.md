# Pokémon Mercury Redux — Sprite curation handoff (2026-10-23)

This repository's Pokédex data and older mobile sprite-audit pages remain unchanged. The active **exception-only design approval** has moved to the dedicated Sprites repository:

- Master reviewer: https://lionsprideemb-tech.github.io/Sprites/master-review.html
- Live review data: https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json
- Protected historical decision ledger: https://github.com/lionsprideemb-tech/Sprites/blob/main/audit/2026-10-23/historical-decisions.json
- Technical/identity-repair queue: https://github.com/lionsprideemb-tech/Sprites/blob/main/audit/2026-10-23/repair-queue.json

## Recovery baseline

- 1,043 historical GBA approval rows retained (566 original KEEP and 477 original CUT).
- 94 later GBA decision rows reconciled, including 27 changed decisions.
- 246 new-import identities matched older rejections; later exported polished choices overrode eight to KEEP and confirmed 238 CUT. All originals are preserved.
- 154 currently actionable candidate-art decisions; 18 technical holds after recovering the user's exported DS and polished artwork choices.
- Fifteen genuine competing-art identities identified; ten remaining review options were already decided in the user's DS export and are no longer repeated.
- Five duplicate historical identity keys retained; two contain contradictory decisions (Hydreigon Mega and Tsareena Mega).

These counts describe overlapping curation ledgers and audits, **not** playable species totals. No Pokédex records, species IDs, evolution methods, type assignments or in-game sprites are altered by this handoff.

## Import gate

The reviewer autosaves locally and exports `mercury-sprite-decisions-v1` JSON and CSV. The user's exported decisions must be reconciled and committed in Sprites before treating them as approved for this Dex. Historical browser-only selections are not silently imported. Do not replace the existing Pokédex roster simply because a candidate appears in the review dataset.

The Sprites reviewer is authoritative for **candidate artwork selection**, not a direct ROM or Dex-integration authorization.

## Recovered original user exports

[Evidence snapshot](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/recovered-user-export-decisions-2026-10-23.json) includes 372 DS-art rows, 262 polished first-pass rows, and 19 follow-up rows. Exact previously chosen front+source identities are preserved as decisions, not returned to the user. Eight polished KEEP choices override older GBA CUT records. Current reviewer: **154 actionable, 18 technical holds**.

## Family regroup and uploaded review export (2026-10-23)

The Sprites master reviewer now uses the verified evolution-family metadata and stage ordering (15 corrected display rows; 75 prior family sections reduced to 69). The user's latest iPhone review export, with 166 choices (154 KEEP / 12 CUT), is archived in [review/user-iphone-decisions-2026-10-23.json](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/user-iphone-decisions-2026-10-23.json). Those user decisions are restored to the reviewer, including newer choices for Mega Lucario Z and Mega Golisopod. The existing game and Pokédex integration state remain unchanged; this is display/approval provenance only.
