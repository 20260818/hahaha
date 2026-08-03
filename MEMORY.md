# Project Memory

## Product Goal

Provide coaches with a compact match-day workbench for confidence building, schedule clarity, lineup and tactic recording, and post-match review.

## Confirmed Decisions

- The primary navigation contains four destinations: Home, Schedule, Tactics, and Energy.
- Opponents and Tasks are removed end-to-end.
- Home prioritizes one confidence prompt, the next match, and the complete tournament schedule.
- The schedule must visibly include August 9 and August 10 even when opponent, time, or stage is still pending.
- Tactics use switchable views rather than a flat layout and record match, period, lineup, tactics, and review notes.
- The Energy page includes a one-card pre-game tarot-inspired MVP that gives supportive action advice and never predicts winning or losing.
- MVP persistence uses browser localStorage.

## Implementation Constraints

- Reuse the existing page style and static-page architecture.
- Keep tarot interpretations curated and deterministic; do not add AI-generated readings in the MVP.
- Do not store secrets in this file.

## Implemented Architecture

- `coach-workbench.html` is the single static application entry point.
- Shared arrays provide the single source of truth for group matches, Shenzhen matches, players, and 12 curated energy cards.
- Score data remains compatible with the existing `coach_scores` localStorage key and `scores.json` crawler output.
- Tactical records use `coach_tactics_v1`; energy selections use `coach_energy_v1` keyed by match and local date.
- The original opponent chart dependency and all opponent/task page state were removed.
- The original energy-card artwork is stored at `assets/energy-card-basketball.png`.

## Validation Snapshot

- Inline JavaScript parsed successfully on 2026-08-03.
- Desktop and 390px mobile browser checks showed no horizontal overflow.
- Browser-tested flows: four-page navigation, score persistence and ranking update, tactical record persistence, five-player/2012-player/A-B duplicate validation, energy-card persistence, and August 9/10 schedule visibility.
- Browser console warnings/errors: none during the final local run.

## External Source

- Current production page: https://20260818.github.io/hahaha/coach-workbench.html
