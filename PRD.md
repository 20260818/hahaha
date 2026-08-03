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

- Show one stable, action-oriented confidence prompt in a light, warm treatment rather than a dark card.
- Show the current preparation target as “本场比赛” with opponent, time, venue, stage, and a countdown precise to the second.
- Show the following Shenzhen match as “下一场比赛” without a competing second-by-second countdown.
- Treat a match as current from its scheduled start until two hours later; outside that window, use the nearest upcoming match as the current preparation target.
- Do not show a separate page introduction or a "daily status suggestion" label above the confidence prompt.
- Do not show the complete schedule on Home; keep it only in the Schedule destination.

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
- Let the coach hold a question privately; the product must not require camera, microphone, motion-sensor, or text input access.
- Show a contained horizontal deck of 78 face-down cards. The coach swipes the deck to shuffle/cut it, then draws the card closest to the center marker.
- Present the deck as a seamless circular strip so no first or last card is ever exposed while swiping in either direction.
- Require at least one deliberate swipe before enabling the draw action.
- Draw from the full 78-card deck with an even chance of upright or reversed orientation.
- Present the card face, orientation, energy theme, confidence cue, team phrase, and concrete action without predicting winning or losing.
- Treat reversed cards as adjustment prompts rather than bad outcomes.
- Persist one card and orientation for each selected match. The coach may review it but cannot redraw for the same match.
- Explain the short interaction flow and keep full rules available without overwhelming the draw stage.
- Do not include secondary coaching stories or generic pre-game leadership content.

## Non-Goals

- Accounts, cloud sync, analytics, AI-generated readings, three-card spreads, camera-based recognition, shake-to-shuffle sensors, minute-level substitutions, video tagging, or remote APIs.

## Acceptance Criteria

- Only four primary navigation items remain.
- August 9 and August 10 remain visible on Schedule.
- Home contains no complete schedule list and shows separate “本场比赛” and “下一场比赛” cards.
- Each main view is reachable and usable with mouse, keyboard, and touch-sized controls.
- Tactical records survive a page refresh and can be removed.
- Offensive and defensive tactics accept custom text, and the lineup strip scrolls without causing page-level horizontal overflow.
- Unstarted group matches do not show score inputs or affect standings.
- The energy card survives refresh for the same match and never displays negative fortune language.
- The energy deck scrolls independently without causing page-level horizontal overflow.
- The energy deck can continue in both directions without exposing a first or last card or changing the logical selected card during a seamless recenter.
- Entering the Energy page downloads only the shared card back; no face image loads until a card is drawn or restored.
- Drawing one card loads only that card face, records upright/reversed orientation, and survives refresh for the same match.
- Reduced-motion users receive an immediate state change without a flip animation.
- Inline scripts parse without syntax errors.
- No retired Opponents or Tasks state/entry points remain.
- Desktop and mobile layouts show no horizontal overflow or blocked primary actions.
