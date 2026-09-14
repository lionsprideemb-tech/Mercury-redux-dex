# Mercury Dex

A static, GitHub Pages-ready Pokédex for **Pokémon Mercury Redux**. It is designed as a fast project reference in the spirit of modern ROM-hack dex browsers, while using Mercury Redux's own roster authority, sprites, Primary/Innate system, moves, and integration status.

## Current data snapshot

- Authority: FINAL R6 / R2 R14-caught-up reconstruction (2026-09-14)
- 1,603 roster entries
- 1,025 canonical entries
- 578 approved Mercury additions
- Current/source-bound and approved-pending entries are distinguished in the UI
- Primary abilities and Innates are shown separately
- Level-up learnsets, base stats, evolution data, source/provenance and project status are shown when source-bound

Approved entries that do not yet have a final source binding are intentionally shown as **Pending Integration** instead of inventing data.

## Features

- Instant full-text search across Pokémon, abilities, Innates, moves, types and source labels
- Filters for type, roster group, source, classification and implementation status
- Name/BST/Dex sorting
- Responsive sprite grid for phone and desktop
- Detailed stats, Primary abilities, Innates, ability descriptions, level-up moves and evolution data
- Current-vs-pending source status
- Favorites stored locally in the browser
- Two-Pokémon compare view
- Shareable direct links using the URL hash
- No framework and no build step: GitHub Pages can serve the repository directly

## GitHub Pages deployment

1. Create a repository (suggested name: `mercury-redux-dex`).
2. Put the contents of this folder at the repository root.
3. In GitHub: **Settings → Pages → Deploy from a branch → `main` / root**.
4. Save. The site will be available from the repository's GitHub Pages URL after deployment finishes.

## Updating the data

`data/pokedex.json` is the generated Mercury data snapshot. Future Mercury source checkpoints should regenerate this file and the relevant `assets/sprites/` files rather than manually editing hundreds of entries.

## Project note

Pokémon is © Nintendo / Creatures / GAME FREAK. Pokémon Mercury Redux and Mercury Dex are non-commercial fan-project tools.
