# Coach Workbench MVP Revision

Date: 2026-08-03

## Objective

Turn the existing information-heavy coach workbench into a match-day tool that helps coaches prepare the team, record lineups and tactics, review games, and deliver supportive pre-game confidence cues.

## Users

- Primary: Shenzhen boys' youth basketball coaching staff.
- Indirect: Players receiving the coach's pre-game guidance.

## Information Architecture

The bottom navigation contains exactly four destinations:

1. Home
2. Schedule
3. Tactics
4. Energy

Opponents and Tasks are removed from navigation, markup, state, and event handling.

## Functional Requirements

### Home

- Show one stable, action-oriented confidence prompt.
- Show the next match with opponent, time, venue, stage, and countdown/status.
- Show the tournament schedule from August 4 through August 10.
- Keep uncertain August 9 and August 10 details visible as pending instead of hiding those dates.

### Schedule

- Provide switchable views for Shenzhen matches, all group matches, and the progression path.
- Keep score entry collapsed until the user opens a match.
- Include August 8, August 9, and August 10 tournament stages.

### Tactics

- Provide switchable views for live records, roster, and the tactic library.
- Record a match, period, first-half A/B segment, five-player lineup, offensive tactic, defensive tactic, and review notes.
- Warn when the lineup does not contain exactly five players.
- Warn when a period has no 2012-born player.
- Warn when first- or second-period A/B lineups repeat players.
- Persist records in localStorage and render a match review timeline.

### Energy

- Put the pre-game energy-card experience first.
- Draw one card from a curated 12-card deck.
- Present a theme, confidence cue, and concrete action without predicting winning or losing.
- Use upright cards only and persist the selected card for the selected match/day.
- Fold existing long-form motivational content under secondary expandable sections.

## Non-Goals

- Accounts, cloud sync, analytics, AI-generated readings, full 78-card deck, reversed cards, three-card spreads, minute-level substitutions, video tagging, or remote APIs.

## Acceptance Criteria

- Only four primary navigation items remain.
- August 9 and August 10 are visible on Home and Schedule.
- Each main view is reachable and usable with mouse, keyboard, and touch-sized controls.
- Tactical records survive a page refresh and can be removed.
- The energy card survives refresh for the same match/day and never displays negative fortune language.
- Inline scripts parse without syntax errors.
- No retired Opponents or Tasks state/entry points remain.
- Desktop and mobile layouts show no horizontal overflow or blocked primary actions.
