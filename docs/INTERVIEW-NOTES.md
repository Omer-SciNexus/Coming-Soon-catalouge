# Interview notes (40 minutes)

Replace every `[...]` with your own facts. Do not claim anything you cannot show.

## Part 1: two slides, at most 2 minutes

**Slide 1: Who I am**
- [Name], full-stack developer, [N] years. React / Next.js / TypeScript, Django + DRF.
- Focus: reusable UI, API contracts, versioned data, self-hosted deployments.
- Working style: small, testable steps; written interface contracts with other engineers.

**Slide 2: Relevant work**
- Django + React task tracker: object-level permissions; proposed tasks stay private until a manager approves.
  (Same idea as your catalogue: draft → approval → publish.)
- JobDockets: Next.js frontend consuming a Laravel API. My part: [your PRs / features].
- This demo: Wagtail StreamField → versioned catalogue assets → two themes, no component code per client.

## Part 2: previous work, 8 minutes

For each project: 30 seconds of what it does, 1 minute of one decision, 1 minute of your own code or commits.
- Task tracker: show the permission check in code, and one commit of yours.
  It is hosted on Vercel because it was a take-home. Say: "It also runs self-hosted with `next build` in
  standalone mode, like this demo." Only say this if you have tried it.
- JobDockets: show your PRs or commits (git log filtered by your name).

## Part 3: practical, 17 minutes

Follow `WALKTHROUGH.md` items 1-4 (about 8 minutes). Keep 6+ minutes for their unannounced change.
For the change: say what you will change before you type, change it, then show the result and run the tests.

## Part 4: technical questions, 9 minutes

**Reusable components and multi-theme**
Components read only semantic CSS variables. Themes are versioned token sets in the database. A website points
at an exact theme version. A test blocks hard-coded colours and fonts in asset files.

**Django/Wagtail integration and API**
StreamField block = asset_id + exact version + props. An adapter makes one stable JSON shape. Next.js renders
on request with `no-store`. Only `live()` pages are sent. Usage events go back to a Django endpoint.

**Database schema, registration, versioning**
Stable identity (Asset) separate from versions (AssetVersion), like your `assets` / `asset_versions` tables.
Approved versions are immutable; changes create a new version. Pages pin versions; there is no "latest" at render time.
Rollback = republish an earlier page revision (Wagtail revisions), which still points to the old versions.

**AI-generated component ingestion and validation**
One API for humans and the AI agent. Steps:
1. Manifest validated against the schema; props_schema must be a valid JSON Schema.
2. Static checks on the code: no `eval`, `new Function`, `dangerouslySetInnerHTML`, network calls, or imports outside an allowlist.
3. Dependencies from an allowlist only, with pinned versions.
4. Isolated build: separate container, no secrets, no network, time and size limits.
5. Tests: render with sample props, accessibility check, screenshots at mobile, tablet and desktop, LTR and RTL.
6. Human approval in the catalogue UI.
7. Publish as an immutable, content-hashed bundle.

Shortcuts I would avoid: loading AI code at runtime in the server process; resolving "latest";
auto-publishing without approval; building on the production server; trusting the AI's own test results.

**Delivery, testing, maintainability**
Contract tests on the JSON shapes shared with the backend and AI engineers (like the adapter test here).
Unit tests for validation and resolution. Visual previews per viewport. Small PRs. Short docs per interface.

**Refactor the existing frontend, or build a separate theme renderer?**
First I would inspect: where colours and fonts are hard-coded; how pages fetch Wagtail data; how the current
theme is built (CSS variables, Tailwind config, styled-components); how many page types exist; what the tests cover.
Usually I would refactor the existing frontend step by step: tokens first, then a block → component registry.
A second rendering system doubles maintenance and splits bug fixes.

**First three days of the project, and a late dependency**
- Day 1: repo access, run everything locally, read the current frontend and Wagtail models. Agree the asset manifest,
  the site API shape and the usage event shape in writing with the backend and AI engineers.
- Day 2: contract tests for those shapes, a token-based theme in the existing frontend, the registry.
- Day 3: the submission endpoint and validation pipeline against the agreed contract, with a fake AI submission.
- If a dependency is late: work against the agreed contract with fixtures and a stub, say so early, and keep the
  integration test ready so it runs the day the real service arrives.

## Part 5: closing, 3 minutes

- Availability: [your hours and time zone]. Start date: [date].
- Ask question 15 from `QUESTIONS.md` (rebuild allowed?) and question 16 (when the AI and backend parts are ready).
- Ask which acceptance demo matters most to them, so the first week targets it.
