# Coming Soon catalogue mini-demo

A small demo for the interview. One Coming Soon page with two tabs and two reusable
assets (ComingSoonHero and UpdatesSignup). Two accounts use the same asset code with
different themes. All themes, assets, versions and pages are **database records**.

```
 Django admin / Wagtail admin            Django + Wagtail (SQLite)              Next.js (renderer)
 ---------------------------    edit    ---------------------------   JSON    ---------------------------
 Theme tokens, Website->Theme  ------>  Theme, Website, Asset,        ------> GET /api/sites/<account>/
 AssetVersion (status, schema)          AssetVersion, ComingSoonPage           tokens -> CSS variables
 Page tabs + blocks (StreamField)       (StreamField) + adapter                blocks -> registry -> React
                                         POST /api/usage/  <------------------ UsageBeacon (analytics ids)
```

- `data/`: the client's sample files (unchanged), plus `wagtail-page.website-02.json` (my demo assumption: a second page for website-02).
- `backend/`: Django + Wagtail. The `catalogue` app holds assets, versions, themes and usage. The `website` app holds websites, the Wagtail page, the StreamField blocks, the adapter and the site API.
- `frontend/`: Next.js renderer. It does not store any data.
- `docs/`: walkthrough, rehearsal steps, questions for the client, file list, interview notes.

## Run it (PowerShell, two terminals)

Terminal 1: backend

```powershell
cd "E:\Work\Demo project\upwork deveo\Project\backend"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Terminal 2: frontend

```powershell
cd "E:\Work\Demo project\upwork deveo\Project\frontend"
npm install
npm run dev
```

Open:

| What | URL |
|---|---|
| Site, account-ocean | http://localhost:3000/?account=account-ocean |
| Site, account-olive, RTL | http://localhost:3000/?account=account-olive&dir=rtl |
| Wagtail admin (pages) | http://127.0.0.1:8000/cms/ |
| Django admin (themes, assets, versions, websites, usage) | http://127.0.0.1:8000/django-admin/ |
| Site API (what Next.js reads) | http://127.0.0.1:8000/api/sites/account-ocean/ |

Forgot the admin password, or cannot log in:

```powershell
cd "E:\Work\Demo project\upwork deveo\Project\backend"
.\.venv\Scripts\python.exe manage.py changepassword <username>
```

If you do not remember the username, or no user exists (for example after a reset), run `createsuperuser` again.
The "Forgotten password?" link on the login page also works: the email is printed in the backend terminal,
not sent. The link in it is split over two lines; remove the `=` at the end of the first line and join them.

`npm run dev` shows code changes at once. `npm start` serves the last `npm run build`, so it shows old code until you build again.

Reset the demo data (stop the backend first):

```powershell
cd "E:\Work\Demo project\upwork deveo\Project\backend"
Remove-Item db.sqlite3
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Tests

```powershell
cd "E:\Work\Demo project\upwork deveo\Project\backend"
.\.venv\Scripts\python.exe manage.py test

cd "E:\Work\Demo project\upwork deveo\Project\frontend"
npm test
npx tsc --noEmit
```

## Self-hosted production build (no Vercel)

`next.config.ts` sets `output: "standalone"`. The build makes a plain Node server.

```powershell
cd "E:\Work\Demo project\upwork deveo\Project\frontend"
$env:DJANGO_URL = "http://127.0.0.1:8000"
npm run build
Copy-Item -Recurse -Force .next\static .next\standalone\.next\static
$env:PORT = "3000"
node .next\standalone\server.js
```

`DJANGO_URL` must be set before the build because the `/api/usage` rewrite is fixed at build time.

## Known limitations

- The registry maps `component_key` to the code in this repo. A real catalogue would map `asset_id@version` to an immutable, built bundle. Today, versions 1.0.0 and 1.1.0 of one asset share the same component code.
- Approved versions cannot change their contract (checked in `AssetVersion.clean()`). That check runs in the admin and the seed, not in the database. A trigger could enforce it (see `docs/QUESTIONS.md`).
- Themes can be edited in place in the admin. In a real system a theme change would be a new theme version.
- Wagtail preview is turned off (the page is headless). A real preview would use Next.js draft mode with a preview token.
- The usage endpoint is public and stores one row per block. It is a stand-in for the backend team's `asset_usage` and analytics work.
- The signup form does not send email addresses anywhere.

## AI disclosure

The first version of this code and these docs was generated with an AI assistant (Claude).
The architecture decisions come from my proposal and my review of the brief.
`docs/CODE-OWNERSHIP.md` explains each file and says which changes I made by hand.
