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

The repository deployment workflow accepts `Mercury_Dex_Payload_R6_2026-09-14.zip` at the repository root. The archive is unpacked automatically for GitHub Pages; no manual extraction is required.

## Updating the data

The generated payload uses 17 gzip+base64 Pokédex shards in `data/pokedex/` and base64 WebP sprite strips in `assets/atlas_strips/`. Future Mercury source checkpoints should regenerate these files rather than hand-editing roster entries.

## Project note

This site is a project-development reference generated from the current Mercury Redux authority. Entries marked **Pending Integration** are intentionally not represented as source-bound mechanics until their final bindings are recovered or implemented.
