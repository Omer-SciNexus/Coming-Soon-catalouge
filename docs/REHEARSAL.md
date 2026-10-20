# Rehearsal: likely live changes

Practise each one by hand, with no AI, until you can do it in under 3 minutes.
Run the frontend with `npm run dev` so code changes reload by themselves.
After practising, reset the data (see README, "Reset the demo data").

Where things are:
- **Django admin** = http://127.0.0.1:8000/django-admin/ (themes, assets, asset versions, websites, usage)
- **Wagtail admin** = http://127.0.0.1:8000/cms/ (pages). Pages are under "Welcome to your new Wagtail site!".
  Both pages are titled "Coming Soon". Hover to see the slug: `coming-soon-website-01` or `coming-soon-website-02`.
- In Wagtail, **Save draft** does not change the site. Only **Publish** does (the API uses `live()`).

---

## 1. Change a theme colour (warm-up, 30 seconds)

1. Django admin → Themes → `theme-olive@1.0.0`.
2. In Design tokens, change `"accent": "#46683d"` to `"accent": "#b0452c"`. Save.
3. Refresh http://localhost:3000/?account=account-olive.

**Expected:** olive badge, accent bar, active tab, button and background glow turn red-brown
(the softer shades follow too, because `color-mix()` derives them from `--accent`). Ocean does not change. No code changed.

## 2. Add an optional `subheading` prop as version 1.1.0, only for website-02

Files and screens, in order:

1. `frontend/components/assets/ComingSoonHero.tsx`:
   - Props type: `type Props = { heading: string; description: string; subheading?: string };`
   - Function arguments: `{ heading, description, subheading }`
   - After the `<h2>`: `{subheading && <p className={styles.subheading}>{subheading}</p>}`
2. `frontend/components/assets/ComingSoonHero.module.css`: add
   ```css
   .subheading {
     color: var(--text);
     font-weight: bold;
     margin-block: 0 0.5rem;
   }
   ```
3. Django admin → Asset versions → **Add**:
   - Asset: `coming-soon-hero`, Version: `1.1.0`, Source: `human`, Status: `approved`, Component key: `ComingSoonHero`
   - Props schema:
     ```json
     {"type": "object", "required": ["heading", "description"], "properties": {"heading": {"type": "string"}, "description": {"type": "string"}, "subheading": {"type": "string"}}, "additionalProperties": false}
     ```
   - Supported directions: `["ltr", "rtl"]`. Save.
4. Wagtail admin → the website-02 page → Announcement tab → the block:
   - Version: open the list. `1.1.0 (coming-soon-hero)` is now there, because it is approved. Pick it.
   - Props: add `, "subheading": "Spring 2027"` inside the JSON object.
   - **Publish**.

**Expected:** olive shows the subheading. Ocean has no subheading and its block still says
`data-asset-version="1.0.0"` (check with the browser inspector). Version 1.0.0 is unchanged.

**What to say:** "1.0.0 was approved, so its contract is locked. I added 1.1.0 next to it.
Only the page that chose 1.1.0 moved. Here both versions share one component file because the
change is backward compatible. In the real catalogue each version would be its own built bundle."

**Bonus:** try to edit the props schema of 1.0.0 in the admin. The save fails:
"Approved versions cannot change props_schema. Create a new version."

**Bonus 2:** add version `1.2.0` with status `draft`. It does not appear in the Wagtail version list.
Pick `1.1.0` for `updates-signup` (it has no 1.1.0): Wagtail refuses with
"No approved or published version with this number." The list is not filtered by asset, so `clean()` checks the pair.

## 3. Add a `radius` token to both themes and use it

The cards already use `border-radius: var(--radius, 1.5rem)`: the theme's `--radius` if it exists, else 1.5rem.

1. Django admin → Themes → `theme-ocean@1.0.0` → add `"radius": "8px"` to the tokens. Save.
2. Same for `theme-olive@1.0.0` with `"radius": "0px"`.
3. Refresh both accounts.

**Expected:** ocean cards have small rounded corners, olive cards are square. No code changed.
`tokensToCssVars` needs no change: `radius` becomes `--radius`.

**If they ask for the input and button too:** `UpdatesSignup.module.css` → in `.input` and `.button`
change `border-radius: 999px;` to `border-radius: var(--radius, 999px);`. `npm test` still passes.

## 4. Add a third account, account-sand

1. Django admin → Themes → **Add**: theme id `theme-sand`, version `1.0.0`, tokens:
   ```json
   {"background": "#f7f0e3", "surface": "#fffaf2", "text": "#3b2f20", "accent": "#a0662a", "button_text": "#ffffff", "border": "#e2d3bb", "font_family": "Trebuchet MS, sans-serif"}
   ```
2. Django admin → Websites → **Add**: website id `website-03`, account id `account-sand`,
   client id `client-01`, theme `theme-sand@1.0.0`.
3. Wagtail admin → the website-01 page → "..." menu → **Copy**. New slug `coming-soon-website-03`,
   tick "Publish copied page" off. Then edit the copy: Website = `website-03`. **Publish**.
4. Open http://localhost:3000/?account=account-sand.
5. Optional code change: add `"account-sand"` to `DEMO_ACCOUNTS` in `frontend/app/page.tsx` so it appears in the switcher.

**Expected:** a third look, same components, no component code changed.

## 5. Set updates-signup to draft and show the placeholder

1. Django admin → Asset versions → `updates-signup@1.0.0` → Status: `draft`. Save.
   (Allowed: status may change; the contract may not.)
2. Open the Updates tab on any account.
3. Wagtail admin → edit a page → add a block: `updates-signup` is no longer in the asset list,
   and the version list shows `1.0.0 (coming-soon-hero)` only.

**Expected:** "Block block-002 is not available (not_renderable_status)." The rest of the page works.
The Next.js terminal shows a `console.warn` with the details. Set the status back to `approved`.

## 6. Switch to RTL

Click **RTL**, or add `&dir=rtl` to the URL. Check both tabs.

**Expected:** the whole site mirrors: badge (dot on the other side), tabs, the hero text
and accent bar (now on the right), the glow circle (top right becomes top left), the input and the button.
No extra CSS, because the assets use logical properties (`inset-inline-end`, `padding-inline`, `text-align: start`).
The dark demo toolbar stays left-to-right on purpose: it is an interview tool, not site content.

## 7. Put an undeclared prop in the page and see validation reject it

1. Wagtail admin → the website-01 page → Announcement → block props.
2. Change to: `{"heading": "Something wonderful is coming", "description": "Our new website is on its way.", "colour": "red"}`
3. **Publish**.

**Expected:** Wagtail refuses to save. The props field shows:
"Additional properties are not allowed ('colour' was unexpected)". Also try removing `"description"`:
"'description' is a required property". Also try broken JSON: "Not valid JSON: ...".

## 8. Change the tab order

1. Wagtail admin → a page → Tabs → on the Updates tab, use the "Move up" arrow.
2. **Publish**. Refresh the site (without `?tab=`).

**Expected:** Updates is now the first tab and is selected by default. No code change.

## 9. Debugging: the backend is down

1. Stop the Django server (Ctrl+C) and refresh the site.

**Expected:** Next.js shows an error page. Its terminal shows `fetch failed` from `getSite` in `frontend/lib/api.ts`.
Explain: the renderer has no data of its own. In production you would add a cached last-good payload
or a friendly error page (`app/error.tsx`). Start Django again and refresh.

## 10. Small code change: a new placeholder text

`frontend/components/CatalogueBlock.tsx` → `Placeholder` → change the text. Test with step 5.
