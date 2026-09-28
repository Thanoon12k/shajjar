# شجّر — Shajjar 🌳

> ازرعها اليوم… وتابع أثرها سنين.

The website for **#شجّر**, the community tree-planting campaign in Mosul and Nineveh. It covers the whole path of a tree:

**طلب → موافقة → توزيع → زراعة → توثيق → متابعة → حماية → قياس الأثر**

The website comes first. The mobile app is planned for later and will reuse the same models.

## Features

| | |
|---|---|
| 🌱 **أريد شجرة** | Step-by-step request form: location type, number of trees, map pin or GPS, watering commitment, up to 5 photos. Each request gets a number such as `SH-1048` and a status timeline. |
| 🗺️ **خريطة شجّر** | OpenStreetMap / Leaflet map of planting sites and individual trees, coloured by health (good, needs follow-up, damaged, forest), with filters and a popup for each site. |
| 🌳 **ملف لكل شجرة** | Each tree has an ID (`SHJ-000124`), a printable QR code, a public profile and a growth timeline. |
| 📸 **شجرتي** | Days since planting, plus a follow-up form (photo, height, health) that updates the tree's record. |
| 🚨 **بلّغ** | Environmental reports with GPS and photos, numbered `ENV-2031`. Reporters can hide their identity. Citizens see three stages 🟡 → 🔵 → 🟢. Reports are rate-limited and fire reports are marked urgent automatically. |
| ⚖️ **اعرف القانون** | Laws on tree cutting and illegal hunting, shown with a clear "needs official legal review" notice. |
| 🌿 **شنو أزرع؟** | Species guide with a simple scoring system for place, sun and water. |
| 🤝 **تطوّع** | Campaigns with join/leave, deadline and capacity rules, and volunteer stats (trees planted, campaigns, hours). |
| 💚 **ساهم** | Contribution methods managed from the admin. There is no payment gateway. |
| 📊 **الأثر ولوحة الفريق** | Real survival-rate numbers (alive ÷ planted), and a team dashboard filtered by city, district and year. |
| ⚙️ **الإدارة** | Arabic Django admin with actions: approve, reject, ready, distributed, and "planted + register trees" (creates the tree IDs). Also verify updates, resolve reports, publish campaigns. Every status change is written to an audit log and sends a notification. |
| 🎨 **5 ثيمات** | غابة الحدباء · دجلة · نبك وطين · رمّان نينوى · ليل الموصل. The choice is saved in the browser, and the night theme follows the system dark mode. |

The site is Arabic-first and right-to-left, works on phones (bottom navigation with a **+** action sheet), respects reduced-motion settings and has no build step.

## Run locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
cp .env.example .env            # DEBUG=true for local
python manage.py migrate
python manage.py seed_shajjar --demo    # real starter content + clearly-labelled demo data
python manage.py createsuperuser
python manage.py runserver
```

Tests: `python manage.py test`. Lint: `ruff check .`

## Deploy (PythonAnywhere)

See [docs/DEPLOY_PYTHONANYWHERE.md](docs/DEPLOY_PYTHONANYWHERE.md).

## Content & data notes

- Sites, species notes, field stories and legal excerpts come from public posts by Anas Al-Taie (`facebook-anas-altaye-last-300-posts.md`). Each one links to its original post.
- Site coordinates are approximate. The team should correct them in the admin.
- The only real tree count seeded is غابة الحدباء (1000 planted, 13 dried). `--demo` adds illustrative counts, fictional users, requests, reports and campaigns. Set `DEMO_MODE=true` to show a banner saying the data is illustrative.
- Legal content is marked as needing official review. Contribution account numbers are never hard-coded; only the organisation adds them, through the admin.
