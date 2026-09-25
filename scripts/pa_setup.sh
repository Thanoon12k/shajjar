#!/bin/bash
# Runs ON PythonAnywhere (via a scheduled task or a Bash console):
#   bash ~/shajjar/scripts/pa_setup.sh
set -e
PA_USER="${PA_USER:-$USER}"
DOMAIN="${PA_DOMAIN:-$(echo "$PA_USER" | tr 'A-Z' 'a-z').pythonanywhere.com}"
PY="${PA_PYTHON:-python3.11}"
cd "$HOME/shajjar/backend"
echo "== $(date) setup for $DOMAIN with $PY"
$PY -m pip install --user --quiet -r requirements.txt
if [ ! -f .env ]; then
  SK=$($PY -c "import secrets;print(secrets.token_urlsafe(50))")
  cat > .env <<ENV
DEBUG=false
SECRET_KEY=$SK
ALLOWED_HOSTS=$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN
SITE_URL=https://$DOMAIN
DEMO_MODE=${DEMO_MODE:-true}
ENV
  echo "created .env"
fi
$PY manage.py migrate --noinput
$PY manage.py collectstatic --noinput -v0
if [ "${SEED:-demo}" = "demo" ]; then $PY manage.py seed_shajjar --demo; else $PY manage.py seed_shajjar; fi
$PY manage.py check --deploy 2>&1 | tail -3 || true
WSGI="/var/www/$(echo "$DOMAIN" | tr '.' '_')_wsgi.py"
[ -f "$WSGI" ] && touch "$WSGI"
echo "== DONE"
