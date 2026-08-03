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
- `tacticsView`: record, roster, or library.
- `selectedMatchId`, `selectedPeriod`, and `selectedSegment` remain local UI state.
- Tactical records persist under a versioned localStorage key.
- Energy-card selections persist under a versioned key derived from match ID and local date.

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

## Energy Card Contract

Each curated card has an ID, name, theme, confidence cue, action, and visual accent. Card selection uses a random browser value on first draw and then persists for the same match/day.

## Interaction and Accessibility

- Primary controls use `button`, `select`, `input`, and `textarea` elements.
- Active tabs expose `aria-selected` or `aria-current`.
- Inputs have visible labels and inline error/status text.
- Focus indicators remain visible.
- Touch targets are at least 44x44px with at least 8px separation where practical.
- Motion respects `prefers-reduced-motion`.

## Verification

1. Parse every inline script with Node.js.
2. Search for retired page IDs, event handlers, and navigation labels.
3. Serve the page with a local HTTP server.
4. Verify all four primary views at desktop and mobile widths.
5. Create a tactical record, refresh, and confirm persistence.
6. Draw an energy card, refresh, and confirm persistence.
7. Confirm August 9 and August 10 appear in rendered content.

## Risks

- Production GitHub Pages source may differ from the fetched page; verify repository/branch before pushing.
- LocalStorage is device-specific and can be cleared; the MVP must describe local-only persistence in the UI.
- Unknown August 9 and August 10 details must remain explicitly pending and should be replaced when official data is available.
