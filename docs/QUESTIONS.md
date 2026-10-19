# Questions for the client

Gaps I found between the sample files and `analytics_machine_component_ai_schema.sql`.
Ask them politely, one or two at a time, in the questions section or at the closing.

## Status and approval

1. The manifest has status `approved`, but `asset_versions.status` has no `approved`
   (it has candidate, validating, validated, published, deprecated, rejected).
   Approval seems to live in `promotion_status` (unreviewed, sandbox, trusted, production, elite, retired).
   **Which field should the renderer trust to decide if a version can appear on a live page?**
2. `assets.status` and `asset_versions.status` have different lists (`assets` has candidate and archived,
   versions has validating and rejected). **Is asset-level status only for the catalogue UI?**
3. Published versions are immutable "by application policy" only.
   **Should the database also enforce it, for example with a trigger that blocks updates to published rows?**

## Identifiers and analytics

4. The Wagtail page id is an integer (101) and `website_id` is a string (`website-01`),
   but `asset_usage.site_id` and `page_id` are uuid. **What ID mapping should analytics use?**
5. `asset_usage` has no column for theme or design-system version, tab, or block.
   **Should `theme_id`, `theme_version`, `tab_id` and `block_id` go into `usage_context` (jsonb)?**
   Also, `instance_id` is a uuid, but Wagtail block ids in the sample are `block-001`.
6. The manifest `asset_id` (`coming-soon-hero`) looks like `assets.slug`, while `assets.id` is a uuid.
   **Is the slug the public, stable ID that pages and the API should use?**

## Themes

7. There is no table linking a website or account to a design system.
   **Where does "website-02 uses theme-olive 1.0.0" live: in your platform's website model, or in a new table?**
8. `design_tokens` uses token paths like `space.section.lg`, but the sample tokens are flat (`button_text`).
   **Will tokens be nested paths in production? My converter would then map `space.section.lg` to `--space-section-lg`.**

## Schema details

9. The manifest's `props_schema` corresponds to `asset_versions.config_schema`. **Same concept, different name?**
10. The manifest meta-schema does not require `additionalProperties: false` inside `props_schema`.
    Without it, unknown props pass validation. **Should it be required?**
11. `component_key` is a fixed enum, so every new component needs a schema release.
    **Is that intended as the allowlist, or should the key come from the registry of built bundles?**
12. `supported_directions` is optional. **If it is missing, is the default LTR only?** (The demo assumes yes.)
13. **Where should text direction live: page, website, or locale?** The demo uses a URL parameter.
14. `assets.default_version_id` exists. **Is it only the default suggestion in the editor's chooser?**
    I would keep pages pinned to an explicit version and never resolve "latest" at render time.

## Delivery

15. When an approved component is new code, **is a rebuild and redeploy of the self-hosted frontend acceptable,
    or must new components become usable without any rebuild?** (This decides the whole delivery design.)
16. **When will the AI agent's submission endpoint and the backend registry tables be ready for integration?**
    The acceptance demos depend on both.
