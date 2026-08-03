# Coach Workbench Project Rules

## Project Scope

- Maintain the Shenzhen youth basketball coach workbench as a lightweight static web page.
- Preserve the existing visual language unless a reviewed product requirement explicitly changes it.
- Keep the implementation dependency-free unless a dependency is demonstrably necessary.

## Working Rules

- Use focused patches and preserve unrelated user changes.
- Use semantic HTML controls, visible focus states, and touch targets of at least 44x44px.
- Store MVP-only user data locally in the browser; do not add accounts, analytics, or remote services without approval.
- Never include credentials or private player data beyond the existing provided roster.

## Validation

- Parse all inline scripts after editing.
- Run focused static checks for retired navigation/page state.
- Verify the main flows in a browser at desktop and mobile widths.
- Confirm schedule, tactical records, and energy-card persistence with representative inputs.

## Deployment

- Preview and verify locally before pushing to GitHub Pages.
- Do not force-push or rewrite unrelated Git history.
