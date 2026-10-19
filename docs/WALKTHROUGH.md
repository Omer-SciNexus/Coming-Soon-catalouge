# Walkthrough: the five things the brief asks to show

Before the call: start both servers, log in to both admins, and open these tabs:
the site (ocean), the site (olive), Wagtail admin, Django admin, the site API, and VS Code.

---

## 1. The page with two tabs and two assets

**Show:** http://localhost:3000/?account=account-ocean, then click **Updates**.
**Open:** `frontend/app/page.tsx` (`Page`), `frontend/components/CatalogueBlock.tsx`.

> "The page is a server component. It loads one JSON payload from Django: account, theme,
> page and the manifests of the asset versions the page uses. Tabs come from `page.tabs`.
> Each tab is a link with `?tab=`, so tabs need no client state and have proper ARIA roles.
> Each block goes through CatalogueBlock, which resolves the asset and renders it."

## 2. Switch account and theme without changing asset code

**Show:** click `account-olive`. Then in Django admin, **Websites → website-02 → theme**:
pick `theme-ocean@1.0.0`, save, refresh the site. Change it back.
**Open:** `frontend/lib/theme.ts` (`tokensToCssVars`), `ComingSoonHero.module.css`,
`backend/website/models.py` (`Website.theme`).

> "The theme is a database record. The website points at an exact theme version.
> Tokens become CSS variables on the page root. Components only use `var(--accent)` and so on.
> A test checks that no asset file has a hex colour or a font-family, so the theming boundary
> cannot break silently. Both accounts render the same component file."

## 3. How StreamField content becomes asset ID, version and props

**Show:** Wagtail admin → Pages → "Welcome to your new Wagtail site!" → the "Coming Soon" page whose
website is website-01 (both pages are titled "Coming Soon"; the slug is `coming-soon-website-01`) → edit.
Open a tab and a block.
Then show http://127.0.0.1:8000/api/sites/account-ocean/.
**Open:** `backend/website/blocks.py` (`CatalogueAssetBlock`, `TabBlock`),
`backend/website/models.py` (`ComingSoonPage.tabs`), `backend/website/adapter.py` (`to_catalogue_page`).

> "The page has a StreamField of tabs. Each tab has a StreamBlock of `catalogue_asset` blocks.
> A block stores asset_id, an exact version and props as JSON text, because Wagtail has no JSON block.
> Wagtail does not produce this API shape by itself, so a small adapter maps the page to exactly
> the shape of your sample file. A test compares the adapter output with `wagtail-page.sample.json`."

## 4. Where input is validated, and how a new approved version becomes selectable

**Open:** `backend/catalogue/validation.py`, `backend/catalogue/models.py` (`AssetVersion.clean`),
`backend/website/blocks.py` (`selectable_assets`, `selectable_versions`, `CatalogueAssetBlock.clean`),
`frontend/lib/catalogue.ts` (`resolveBlock`).

> "Validation happens in three places.
> One: when an asset version enters the catalogue, its manifest is checked against your manifest
> schema, and its props_schema must itself be a valid JSON Schema. An approved version cannot
> change its contract; you create a new version.
> Two: when an editor saves a page, the block checks that the version is approved or published
> and that the props match that version's props_schema.
> Three: when the page renders, the renderer checks again and fails closed. One bad block shows a
> placeholder; the page never crashes.
> A new version becomes selectable as soon as its status is approved: it appears in the editor's
> version list, with the assets that have it. Draft, validated and rejected versions are never listed.
> Existing pages do not move: they keep the exact version they pinned until an editor changes it
> and publishes again."

**Show it live (1 minute):** Django admin → add `coming-soon-hero` 1.1.0 as approved (same schema as 1.0.0) →
Wagtail edit page → open the version list: `1.1.0 (coming-soon-hero)` is there. Do not publish. Delete 1.1.0 after.

**Rebuild or runtime?** (they will probably ask)

> "Data changes at runtime, code changes through a build. Themes, tokens, page composition and
> choosing an approved version are data: no rebuild. A brand-new component is code: after approval,
> an isolated build makes an immutable bundle, then the self-hosted frontend redeploys. Pinned
> pages do not change. I would not load AI-generated JavaScript at runtime inside the server process."

## 5. What I need from your Django/Wagtail engineer, and where analytics identifiers travel

**Open:** `frontend/components/CatalogueBlock.tsx` (the `data-*` attributes),
`frontend/components/UsageBeacon.tsx`, `backend/catalogue/views.py` (`record_usage`).
**Show:** Django admin → Asset usage events, after clicking around the site.

> "Each rendered block carries block_id, asset_id, asset_version, website_id, page_id, tab_id,
> theme_id and theme_version. The beacon sends one batched event to /api/usage, which Next
> forwards to Django. Django checks the asset version exists and stores one row per block.
> In your system that endpoint belongs to the backend engineer and writes asset_usage."

What I need from your backend engineer:

1. A stable site API per website (or per account) with this page shape, and the decision on where theme assignment lives (there is no website→design_system table in the SQL yet).
2. The ID mapping for analytics: the Wagtail page id is an integer and the sample website_id is a string, but `asset_usage.site_id` and `page_id` are uuid.
3. Which status the renderer should trust: `status` or `promotion_status`.
4. One submission endpoint for humans and the AI agent, writing `assets`, `asset_versions` and `asset_files`, with validation results stored in `asset_tests`.
5. A webhook or job when a version is approved, to start the isolated build.
