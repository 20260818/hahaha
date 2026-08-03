# Project Memory

## Product Goal

Provide coaches with a compact match-day workbench for confidence building, schedule clarity, lineup and tactic recording, and post-match review.

## Confirmed Decisions

- The primary navigation contains four destinations: Home, Schedule, Tactics, and Energy.
- Opponents and Tasks are removed end-to-end.
- Home prioritizes one confidence prompt, the next match, and the complete tournament schedule.
- Home has no visible page intro or "今日状态暗示" label; its next-match countdown is precise to the second.
- The schedule must visibly include August 9 and August 10 even when opponent, time, or stage is still pending.
- Unstarted matches do not expose score inputs or contribute stored/external scores to standings.
- Tactics switch only between live records and the roster; tactic names are free text and lineup choices use a horizontal scroll strip.
- The Energy page includes a one-card pre-game tarot-inspired MVP that gives supportive action advice and never predicts winning or losing.
- The tarot MVP uses 12 upright cards, one persisted card per match/day, no good/bad classification, and action-oriented interpretations; generic coaching-story sections are excluded.
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

- Inline JavaScript parsed successfully on 2026-08-03 after the second UI revision.
- Desktop and 390px mobile browser checks showed no horizontal overflow; the lineup strip scrolls independently at both widths.
- Browser-tested flows: four-page navigation, one-second countdown updates, pre-start score gating with stale scores excluded from standings, free-text tactic entry, tactical validation/persistence, refined five-rule energy-card guidance, energy-card persistence, and August 9/10 schedule visibility.
- Browser console warnings/errors: none during the final local run.

## External Source

- Current production page: https://20260818.github.io/hahaha/coach-workbench.html
