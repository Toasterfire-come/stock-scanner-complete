#!/usr/bin/env bash
set -euo pipefail

# Transfer both Django databases (default=user, stocks=stock/news) from LOCAL -> REMOTE.
#
# Remote targets are taken from your existing DB_* and DB2_* env (or .env):
#   - DB_*   => remote default DB (users/auth/etc.)
#   - DB2_*  => remote stocks DB (stocks + news)
#
# Local sources can be provided via LOCAL_DB_* and LOCAL_DB2_*; if omitted, sensible
# localhost defaults are used (127.0.0.1, root, no password, 3306, names: stockscanner/stocks).
#
# Prefers mysqldump for speed; falls back to Django dumpdata/loaddata automatically.
#
# Usage:
#   cd backend
#   export DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
#   # Ensure your .env holds DB_* and DB2_* for the REMOTE servers (already set)
#   # Optionally set LOCAL_DB_* and LOCAL_DB2_* for your local MySQL
#   ./scripts/transfer_data.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

require_env() {
  local name="$1"
  if [ -z "${!name:-}" ]; then
    echo "Missing required env: $name" >&2
    exit 1
  fi
}

load_local_env() {
  # Source .env if present to populate DB_* vars
  if [ -f .env ]; then
    set -o allexport
    # shellcheck disable=SC1091
    source .env
    set +o allexport
  fi
}

transfer_mysql_db() {
  local local_host="$1" local_name="$2" local_user="$3" local_pass="$4" local_port="${5:-3306}"
  local remote_host="$6" remote_name="$7" remote_user="$8" remote_pass="$9" remote_port="${10:-3306}"

  echo "Transferring MySQL database '$local_name' -> '$remote_name'..."

  # Use env var for password to avoid exposing in process list
  MYSQL_PWD_LOCAL="$local_pass" MYSQL_PWD_REMOTE="$remote_pass"
  export MYSQL_PWD="$MYSQL_PWD_LOCAL"

  # Create dump
  DUMP_FILE="/tmp/${local_name}_dump_$(date +%s).sql"
  mysqldump --single-transaction --quick --skip-lock-tables \
    -h "$local_host" -P "$local_port" -u "$local_user" "$local_name" > "$DUMP_FILE"

  # Import to remote
  export MYSQL_PWD="$MYSQL_PWD_REMOTE"
  mysql -h "$remote_host" -P "$remote_port" -u "$remote_user" "$remote_name" < "$DUMP_FILE"

  rm -f "$DUMP_FILE"
  echo "Transfer complete for '$local_name'."
}

transfer_via_django() {
  echo "mysqldump not available. Falling back to Django dumpdata/loaddata fixtures..."

  # Remote targets must be present via DB_* and DB2_*
  require_env DB_HOST; require_env DB_NAME; require_env DB_USER; require_env DB_PASSWORD
  require_env DB2_HOST; require_env DB2_NAME; require_env DB2_USER; require_env DB2_PASSWORD

  # Dump LOCAL databases by overriding env to point Django to local sources
  echo "Dumping LOCAL default DB via Django..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB_HOST="$LOCAL_DB_HOST" DB_NAME="$LOCAL_DB_NAME" DB_USER="$LOCAL_DB_USER" DB_PASSWORD="$LOCAL_DB_PASSWORD" DB_PORT="$LOCAL_DB_PORT"
    # Ensure local stocks DB is configured
    export DB2_HOST="$LOCAL_DB2_HOST" DB2_NAME="$LOCAL_DB2_NAME" DB2_USER="$LOCAL_DB2_USER" DB2_PASSWORD="$LOCAL_DB2_PASSWORD" DB2_PORT="$LOCAL_DB2_PORT"
    python manage.py dumpdata --database=default \
      --exclude=contenttypes --exclude=auth.permission --exclude=sessions.Session \
      --natural-foreign --natural-primary --indent 2 > /tmp/default_data.json
  )

  echo "Dumping LOCAL stocks DB via Django (apps: stocks, news)..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB_HOST="$LOCAL_DB_HOST" DB_NAME="$LOCAL_DB_NAME" DB_USER="$LOCAL_DB_USER" DB_PASSWORD="$LOCAL_DB_PASSWORD" DB_PORT="$LOCAL_DB_PORT"
    export DB2_HOST="$LOCAL_DB2_HOST" DB2_NAME="$LOCAL_DB2_NAME" DB2_USER="$LOCAL_DB2_USER" DB2_PASSWORD="$LOCAL_DB2_PASSWORD" DB2_PORT="$LOCAL_DB2_PORT"
    python manage.py dumpdata --database=stocks stocks news \
      --natural-foreign --natural-primary --indent 2 > /tmp/stocks_data.json
  )

  # Load into REMOTE by ensuring DB_* and DB2_* (already set) are used
  echo "Loading fixtures into REMOTE default DB..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB_HOST="$DB_HOST" DB_NAME="$DB_NAME" DB_USER="$DB_USER" DB_PASSWORD="$DB_PASSWORD" DB_PORT="${DB_PORT:-3306}"
    python manage.py loaddata --database=default /tmp/default_data.json --ignorenonexistent
  )

  echo "Loading fixtures into REMOTE stocks DB..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB2_HOST="$DB2_HOST" DB2_NAME="$DB2_NAME" DB2_USER="$DB2_USER" DB2_PASSWORD="$DB2_PASSWORD" DB2_PORT="${DB2_PORT:-3306}"
    python manage.py loaddata --database=stocks /tmp/stocks_data.json --ignorenonexistent
  )

  echo "Fixture-based transfer complete."
}

main() {
  load_local_env

  # Resolve local DBs from env (allow overrides via LOCAL_* if set)
  LOCAL_DB_HOST="${LOCAL_DB_HOST:-${DB_HOST:-127.0.0.1}}"
  LOCAL_DB_NAME="${LOCAL_DB_NAME:-${DB_NAME:-stockscanner}}"
  LOCAL_DB_USER="${LOCAL_DB_USER:-${DB_USER:-root}}"
  LOCAL_DB_PASSWORD="${LOCAL_DB_PASSWORD:-${DB_PASSWORD:-}}"
  LOCAL_DB_PORT="${LOCAL_DB_PORT:-${DB_PORT:-3306}}"

  LOCAL_DB2_HOST="${LOCAL_DB2_HOST:-${DB2_HOST:-$LOCAL_DB_HOST}}"
  LOCAL_DB2_NAME="${LOCAL_DB2_NAME:-${DB2_NAME:-stocks}}"
  LOCAL_DB2_USER="${LOCAL_DB2_USER:-${DB2_USER:-$LOCAL_DB_USER}}"
  LOCAL_DB2_PASSWORD="${LOCAL_DB2_PASSWORD:-${DB2_PASSWORD:-$LOCAL_DB_PASSWORD}}"
  LOCAL_DB2_PORT="${LOCAL_DB2_PORT:-${DB2_PORT:-$LOCAL_DB_PORT}}"

  # Remote targets come from DB_* and DB2_* in env/.env (already set)
  require_env DB_HOST; require_env DB_NAME; require_env DB_USER; require_env DB_PASSWORD
  require_env DB2_HOST; require_env DB2_NAME; require_env DB2_USER; require_env DB2_PASSWORD

  if have_cmd mysqldump && have_cmd mysql; then
    transfer_mysql_db "$LOCAL_DB_HOST" "$LOCAL_DB_NAME" "$LOCAL_DB_USER" "$LOCAL_DB_PASSWORD" "$LOCAL_DB_PORT" \
                      "$DB_HOST" "${DB_NAME}" "${DB_USER}" "${DB_PASSWORD}" "${DB_PORT:-3306}"

    transfer_mysql_db "$LOCAL_DB2_HOST" "$LOCAL_DB2_NAME" "$LOCAL_DB2_USER" "$LOCAL_DB2_PASSWORD" "$LOCAL_DB2_PORT" \
                      "$DB2_HOST" "${DB2_NAME}" "${DB2_USER}" "${DB2_PASSWORD}" "${DB2_PORT:-3306}"
  else
    transfer_via_django
  fi
}

main "$@"

