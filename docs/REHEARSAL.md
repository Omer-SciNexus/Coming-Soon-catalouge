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

## 2. Add an optional `subheading` prop as version 1.3.0, only for website-02

(1.1.0 and 1.2.0 already exist: the image version and the document version from `data/`, see steps 11 and 12.)

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
   - Asset: `coming-soon-hero`, Version: `1.3.0`, Source: `human`, Status: `approved`, Component key: `ComingSoonHero`
   - Props schema: the 1.2.0 schema plus `subheading`:
     ```json
     {"type": "object", "required": ["heading", "description"], "properties": {"heading": {"type": "string"}, "description": {"type": "string"}, "image_url": {"type": "string", "pattern": "^(https?://|/(?!/))\\S+$"}, "image_alt": {"type": "string"}, "document_url": {"type": "string", "pattern": "^(https?://|/(?!/))\\S+$"}, "document_label": {"type": "string"}, "subheading": {"type": "string"}}, "additionalProperties": false}
     ```
   - Supported directions: `["ltr", "rtl"]`. Save.
4. Wagtail admin → the website-02 page → Announcement tab → the block:
   - Version: open the list. `1.3.0 (coming-soon-hero)` is now there, because it is approved. Pick it.
   - Props: add `, "subheading": "Spring 2027"` inside the JSON object.
   - **Publish**.

**Expected:** olive shows the subheading. Ocean has no subheading and its block still says
`data-asset-version="1.0.0"` (check with the browser inspector). Version 1.0.0 is unchanged.

**What to say:** "1.0.0 was approved, so its contract is locked. I added 1.3.0 next to it.
Only the page that chose 1.3.0 moved. Here both versions share one component file because the
change is backward compatible. In the real catalogue each version would be its own built bundle."

**Bonus:** try to edit the props schema of 1.0.0 in the admin. The save fails:
"Approved versions cannot change props_schema. Create a new version."

**Bonus 2:** add version `1.4.0` with status `draft`. It does not appear in the Wagtail version list.
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
5. The switcher now shows an `account-sand` button by itself. It lists every account with a
   published page (`GET /api/sites/`), so no code change is needed.

**Expected:** a third look, same components, no component code changed.

**Bonus:** publish the copy while its Website is still `website-01`. Wagtail refuses:
'website-01 already has a live page: "Coming Soon". Unpublish that page first, or pick another website.'
The API sends one live page per website, so a second one would be hidden. Save draft is still allowed.

## 5. Set updates-signup to draft and show the placeholder

1. Django admin → Asset versions → `updates-signup@1.0.0` → Status: `draft`. Save.
   (Allowed: status may change; the contract may not.)
2. Open the Updates tab on any account.
3. Wagtail admin → edit a page → add a block: `updates-signup` is no longer in the asset list,
   and in the version list `1.0.0` says `(coming-soon-hero)` only (no more `updates-signup`).

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

## 11. Add an image to the hero (version 1.1.0)

1. Wagtail admin → **Images** → **Add an image** → upload a photo.
2. Open the image. Right-click the preview → **Copy image address**. Keep only the part from `/media/`,
   for example `/media/images/photo.max-800x600.jpg`.
3. Wagtail admin → the website-02 page → Announcement tab → the hero block:
   - Version: `1.1.0 (coming-soon-hero)`.
   - Props: add `, "image_url": "/media/images/photo.max-800x600.jpg", "image_alt": "Our new shop"`.
   - **Publish**.

**Expected:** olive shows the photo next to the text (under it on a phone; on the left in RTL).
Ocean stays on 1.0.0 and has no image. Next.js forwards `/media/` to Django (`next.config.ts`).

**Bonus:** put `"image_url": "javascript:alert(1)"` in the props. Wagtail refuses it (the 1.1.0 schema
only allows `http(s)://` or `/...`), and the renderer would ignore it anyway (`isSafeUrl`).

## 12. Add a download link for a PDF (version 1.2.0)

1. Wagtail admin → **Documents** → **Add a document** → upload a PDF.
2. Open it. The file link on the edit page looks like `http://127.0.0.1:8000/documents/1/brochure.pdf`.
   Keep the part from `/documents/`: `/documents/1/brochure.pdf`.
3. Wagtail admin → the website-02 page → Announcement tab → the hero block:
   - Version: `1.2.0 (coming-soon-hero)`.
   - Props: add `, "document_url": "/documents/1/brochure.pdf", "document_label": "Download the brochure"`.
     (Keep `image_url` too if you want the image; 1.2.0 has both.)
   - **Publish**.

**Expected:** an outlined button with a download arrow under the text, in the theme's accent colour.
It opens the PDF in a new tab. Without `document_label` it says "Download".
Documents are served by a Django view, so unlike images they also work in Docker.
