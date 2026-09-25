# Deploying Shajjar to PythonAnywhere

Live at: **https://shajjar.pythonanywhere.com/** (account `SHAJJAR`)

## Automated (from any machine)

```bash
export PA_API_TOKEN=xxxxxxxx          # PythonAnywhere → Account → API token
python scripts/deploy_pythonanywhere.py --user SHAJJAR --setup
```

What the script does:

1. Uploads `backend/` and `scripts/` to `/home/SHAJJAR/shajjar/`. It never uploads `.env`, the database or media.
2. Creates the web app `shajjar.pythonanywhere.com` (Python 3.11) if it doesn't exist yet, and turns on forced HTTPS.
3. Maps static files: `/static/` → `backend/staticfiles`, `/media/` → `backend/media`.
4. Writes the WSGI file.
5. With `--setup`, schedules `scripts/pa_setup.sh` to run about 2 minutes later. Free accounts can't drive consoles through the API, so a scheduled task does the work instead. The setup script:
   - runs `pip install --user`
   - creates `.env` on the server with a random `SECRET_KEY` and `DEBUG=false`
   - runs `migrate`, `collectstatic` and `seed_shajjar --demo`
   - reloads the site.

   The output goes to `/home/SHAJJAR/shajjar_setup.log`, which also contains the generated team login. Delete the scheduled task afterwards; it runs daily and is harmless but unnecessary.

To update the code later, run `python scripts/deploy_pythonanywhere.py --user SHAJJAR`. After a model change, open a Bash console and run `cd ~/shajjar/backend && python3.11 manage.py migrate`.

## Manual (Bash console on PythonAnywhere)

```bash
git clone https://github.com/Thanoon12k/shajjar.git ~/shajjar
bash ~/shajjar/scripts/pa_setup.sh          # SEED=real for no demo data, DEMO_MODE=false to hide the banner
```

Then, on the **Web** tab:

- Source code: `/home/SHAJJAR/shajjar/backend`
- WSGI file content: see `scripts/deploy_pythonanywhere.py`
- Static files: `/static/` → `/home/SHAJJAR/shajjar/backend/staticfiles`, `/media/` → `/home/SHAJJAR/shajjar/backend/media`
- Click **Reload**.

## Going from demo to real data

1. In the admin, delete the demo users (`*@shajjar.demo`); their requests and reports are deleted with them.
2. Enter the real counts and photos for each site (before/after images turn on the comparison slider).
3. Set `DEMO_MODE=false` in `backend/.env`, then reload.
4. Create real team accounts: `python3.11 manage.py createsuperuser`.

## Notes

- The database is SQLite, which fits the free plan. For MySQL, set `DB_ENGINE=django.db.backends.mysql` and the `DB_*` variables in `.env`, then run `pip install --user mysqlclient`.
- Free accounts can only call allow-listed external sites from the server. The site makes no server-side external calls; maps, fonts and Leaflet load in the visitor's browser.
