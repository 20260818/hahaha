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
- Show the next match with opponent, time, venue, stage, and a countdown precise to the second.
- Do not show a separate page introduction or a "daily status suggestion" label above the confidence prompt.
- Show the tournament schedule from August 4 through August 10.
- Keep uncertain August 9 and August 10 details visible as pending instead of hiding those dates.

### Schedule

- Provide switchable views for Shenzhen matches, all group matches, and the progression path.
- Do not expose score inputs or include stored scores in standings before the scheduled start time.
- After the scheduled start time, keep score entry collapsed until the user opens a match.
- Include August 8, August 9, and August 10 tournament stages.

### Tactics

- Provide switchable views for live records and the roster; the tactic library is out of scope.
- Record a match, period, first-half A/B segment, five-player lineup, offensive tactic, defensive tactic, and review notes.
- Let coaches enter offensive and defensive tactics as free text.
- Present lineup choices as a horizontal swipe/scroll strip instead of a flat grid.
- Warn when the lineup does not contain exactly five players.
- Warn when a period has no 2012-born player.
- Warn when first- or second-period A/B lineups repeat players.
- Persist records in localStorage and render a match review timeline.

### Energy

- Put the pre-game energy-card experience first.
- Draw one card from a curated 12-card deck.
- Present a theme, confidence cue, and concrete action without predicting winning or losing.
- Use upright cards only and persist the selected card for the selected match/day.
- Explain the five MVP rules in the page: choose a match and question, one card per match/day, 12 upright cards, no outcome/score/injury prediction, and action-oriented interpretation of reminder cards.
- Do not include secondary coaching stories or generic pre-game leadership content.

## Non-Goals

- Accounts, cloud sync, analytics, AI-generated readings, full 78-card deck, reversed cards, three-card spreads, minute-level substitutions, video tagging, or remote APIs.

## Acceptance Criteria

- Only four primary navigation items remain.
- August 9 and August 10 are visible on Home and Schedule.
- Each main view is reachable and usable with mouse, keyboard, and touch-sized controls.
- Tactical records survive a page refresh and can be removed.
- Offensive and defensive tactics accept custom text, and the lineup strip scrolls without causing page-level horizontal overflow.
- Unstarted group matches do not show score inputs or affect standings.
- The energy card survives refresh for the same match/day and never displays negative fortune language.
- Inline scripts parse without syntax errors.
- No retired Opponents or Tasks state/entry points remain.
- Desktop and mobile layouts show no horizontal overflow or blocked primary actions.
