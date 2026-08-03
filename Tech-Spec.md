# Coach Workbench Technical Specification

Date: 2026-08-03

## Architecture

- Preserve a single static HTML deliverable with embedded CSS and JavaScript.
- Use semantic HTML and dependency-free browser APIs.
- Use data arrays as the source of truth for matches, players, tactics, confidence prompts, and energy cards.
- Render page content from those arrays rather than duplicating schedule facts in markup.

## State

- `activePage`: home, schedule, tactics, or energy.
- `scheduleView`: team, group, or path.
- `tacticsView`: record or roster.
- `selectedMatchId`, `selectedPeriod`, and `selectedSegment` remain local UI state.
- Tactical records persist under a versioned localStorage key.
- Energy-card selections persist under `coach_energy_v2`, keyed only by match ID so a match cannot be redrawn on a later date.

## Home Match Pair

- `getHomeMatchPair()` selects the current and following Shenzhen matches from `TEAM_MATCHES`.
- A match remains current from its scheduled start until two hours later; otherwise the nearest upcoming match becomes the current preparation target.
- Only the current match receives a second-by-second countdown. The following match remains visually secondary.
- Home does not render a schedule list; complete tournament dates remain available in Schedule.

## Tactical Record Contract

```ts
interface TacticalRecord {
  id: string;
  matchId: string;
  period: 1 | 2 | 3 | 4;
  segment: "A" | "B" | null;
  playerIds: string[];
  offenseTactic: string;
  defenseTactic: string;
  notes: string;
  updatedAt: string;
}
```

The browser implementation validates loaded records before using them and falls back to an empty list on malformed storage.

## Energy Deck Contract

```ts
type TarotOrientation = "upright" | "reversed";

interface TarotCard {
  id: string;
  file: string;
  name: string;
  upright: TarotReading;
  reversed: TarotReading;
}

interface TarotReading {
  theme: string;
  message: string;
  teamPhrase: string;
  action: string;
}

interface EnergySelection {
  cardId: string;
  orientation: TarotOrientation;
  drawnAt: string;
}
```

- The 22 Major Arcana cards use individually curated supportive readings.
- Minor Arcana readings combine curated suit and rank guidance so all 56 cards remain distinct without an unmaintainable duplicated data block.
- Reversed readings describe adjustment, attention, or a different use of the same energy; they never predict failure.
- Initial deck order and orientation use browser cryptographic randomness when available, with `Math.random` as a compatibility fallback.

## Energy Interaction

1. Build a shuffled in-memory order for all 78 cards.
2. Render three consecutive copies of the shuffled 78-card order inside one contained horizontal scroller; all 234 card backs reuse one cached asset.
3. Start in the middle copy and silently recenter to the equivalent position whenever scrolling enters an outer copy, producing a seamless circular strip.
4. Convert the centered rendered index to a logical card index with modulo 78 so recentering never changes the selected card.
5. Track a deliberate pointer/touch/keyboard scroll before enabling draw.
6. On draw, select the logical card closest to the center marker.
7. Assign the selected face image only after draw, wait for image decoding, then reveal it.
8. Persist the card ID, orientation, and draw timestamp by match ID.
9. Restore the same result on refresh without rendering or downloading the other 77 faces.

## Tarot Assets

- Source: the user-authorized `highlig/ricky-wahite-tarot` image set.
- Convert the 78 source PNG files to 420px-wide WebP files before adding them to the site.
- Keep source PNG files outside the production asset tree.
- Do not hotlink GitHub raw URLs at runtime.
- Use one optimized local card-back asset for the full scroll deck.
- The Energy page should add less than 300 KB to its initial transfer and less than 150 KB for a typical first reveal.

## Interaction and Accessibility

- Primary controls use `button`, `select`, `input`, and `textarea` elements; tactic names use labeled text inputs.
- Active tabs expose `aria-selected` or `aria-current`.
- Inputs have visible labels and inline error/status text.
- Focus indicators remain visible.
- Touch targets are at least 44x44px with at least 8px separation where practical.
- The lineup selector uses a contained horizontal scroll strip with scroll snapping and must not increase the document width.
- The tarot deck is the only intentional horizontal gesture region on the Energy page. It uses `overscroll-behavior-inline: contain`, visible instructions, a center marker, and a non-gesture draw button.
- Motion respects `prefers-reduced-motion`.

## Visual System

- Use a warm sports-tool palette: warm ivory background, white surfaces, energetic orange primary actions, trust blue secondary states, and deep blue-gray body text.
- The confidence cue uses a light amber/orange gradient with dark text; no black or near-black motivational panel.
- Keep the tarot stage as a contained deep-indigo exception for ritual focus rather than applying dark surfaces across the application.
- Preserve readable contrast, visible focus rings, and restrained shadows.

## Time-Gated Behavior

- The current-match countdown updates once per second and renders `days + HH:MM:SS` when at least one full day remains, otherwise `HH:MM:SS`.
- Group-match score forms render only when the scheduled start timestamp is not in the future.
- Standings and optional `scores.json` hydration ignore scores for matches whose scheduled start timestamp is still in the future.

## Verification

1. Parse every inline script with Node.js.
2. Search for retired page IDs, event handlers, and navigation labels.
3. Serve the page with a local HTTP server.
4. Verify all four primary views at desktop and mobile widths.
5. Create a tactical record, refresh, and confirm persistence.
6. Draw an energy card, refresh, and confirm persistence.
7. Confirm August 9 and August 10 appear in Schedule and that Home contains no complete schedule list.
8. Confirm an unstarted group match has no score inputs and does not change standings even if stale local score data exists.
9. Confirm the countdown changes every second and the lineup strip scrolls independently at desktop and mobile widths.
10. Confirm the Energy page does not request camera, microphone, motion, or location permission.
11. Confirm the deck requires a swipe, can continue through both boundaries without exposing an end, the center logical card draws, and the same card/orientation persists after refresh and match switching.
12. Confirm no more than one tarot face image is loaded in a fresh draw flow.
13. Verify desktop, 390px mobile, 375px mobile, landscape, keyboard operation, and reduced-motion behavior.

## Risks

- Production GitHub Pages source may differ from the fetched page; verify repository/branch before pushing.
- LocalStorage is device-specific and can be cleared; the MVP must describe local-only persistence in the UI.
- Unknown August 9 and August 10 details must remain explicitly pending and should be replaced when official data is available.
- The authorized third-party card artwork may have attribution requirements; keep the source credit visible and preserve any terms supplied by the rights holder.
