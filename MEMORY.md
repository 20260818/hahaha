# Project Memory

## Product Goal

Provide coaches with a compact match-day workbench for confidence building, schedule clarity, lineup and tactic recording, and post-match review.

## Confirmed Decisions

- The primary navigation contains four destinations: Home, Schedule, Tactics, and Energy.
- Opponents and Tasks are removed end-to-end.
- Home prioritizes one light confidence prompt, the current preparation match, and the following match. The complete tournament schedule appears only in Schedule.
- Home has no visible page intro or "今日状态暗示" label; its next-match countdown is precise to the second.
- The schedule must visibly include August 9 and August 10 even when opponent, time, or stage is still pending.
- Unstarted matches do not expose score inputs or contribute stored/external scores to standings.
- Tactics switch only between live records and the roster; tactic names are free text and lineup choices use a horizontal scroll strip.
- The Energy page includes a one-card pre-game tarot-inspired MVP that gives supportive action advice and never predicts winning or losing.
- The user confirmed authorization to use the `highlig/ricky-wahite-tarot` image set. The MVP uses the full 78-card deck, horizontal swipe-to-shuffle, a center-card draw, and equal upright/reversed orientation probability.
- The tarot deck is visually circular: three lightweight copies of the shuffled order start from the middle copy and recenter to an equivalent logical card before either outer boundary is exposed.
- Reversed cards are framed as adjustment prompts rather than bad outcomes. Each match keeps one card and orientation permanently in the current browser; generic coaching-story sections and camera/motion-sensor shuffling are excluded.
- MVP persistence uses browser localStorage.

## Implementation Constraints

- Reuse the existing page style and static-page architecture.
- Keep tarot interpretations curated and deterministic; do not add AI-generated readings in the MVP.
- Do not store secrets in this file.

## Implemented Architecture

- `coach-workbench.html` is the single static application entry point.
- Shared arrays provide the single source of truth for group matches, Shenzhen matches, players, 22 individually curated Major Arcana cards, and 56 Minor Arcana cards composed from curated suit/rank guidance.
- Score data remains compatible with the existing `coach_scores` localStorage key and `scores.json` crawler output.
- Tactical records use `coach_tactics_v1`; energy selections use `coach_energy_v2` keyed only by match ID.
- The original opponent chart dependency and all opponent/task page state were removed.
- Tarot assets are 78 locally hosted 420px-wide WebP faces plus one shared WebP card back under `assets/tarot/`; runtime does not hotlink GitHub or ship the source PNG files.
- The visual system uses a warm ivory background, white surfaces, deep accessible orange primary buttons, trust-blue secondary states, and deep blue-gray text. The tarot stage remains the only intentionally dark surface.

## Validation Snapshot

- Inline JavaScript parsed successfully on 2026-08-03 after the second UI revision.
- Desktop and 390px mobile browser checks showed no horizontal overflow; the lineup strip scrolls independently at both widths.
- Browser-tested flows: four-page navigation, one-second countdown updates, pre-start score gating with stale scores excluded from standings, free-text tactic entry, tactical validation/persistence, refined five-rule energy-card guidance, energy-card persistence, and August 9/10 schedule visibility.
- Browser console warnings/errors: none during the final local run.
- Tarot browser checks covered an empty 78-card deck, disabled pre-shuffle draw, keyboard and horizontal-scroll shuffling, center-card draw, upright/reversed result rendering, focus transfer, refresh persistence, match-specific locking, and one-face-image DOM loading.
- Responsive tarot checks at 1280px, 390px, 375px, and 844x390 showed no document-level horizontal overflow; the fixed bottom navigation retains 100px clearance after the rules card.
- The optimized tarot directory contains 79 WebP files at about 6.1 MB total; every individual face is below 150 KB and the shared back is about 25 KB.
- Home browser checks confirmed separate “本场比赛” and “下一场比赛” cards, a second-level current-match countdown, no Home schedule rows, and retained August 9/10 dates in Schedule.
- Circular-deck browser checks confirmed 234 rendered card-back elements representing 78 logical cards, middle-copy initialization, logical-index preservation across left recentering, keyboard/touch-style horizontal operation, and no document-level overflow at 1280px, 390px, 375px, or 844x390.

## External Source

- Current production page: https://20260818.github.io/hahaha/coach-workbench.html
- User-authorized tarot source: https://github.com/highlig/ricky-wahite-tarot
