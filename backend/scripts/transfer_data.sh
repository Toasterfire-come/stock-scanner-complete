#!/usr/bin/env bash
set -euo pipefail

# Transfer both Django databases (default=user, stocks=stock/news) from local to remote.
# Prefers mysqldump for speed; falls back to Django dumpdata/loaddata if mysqldump is unavailable.
#
# Usage (env-driven):
#   cd backend
#   export DJANGO_SETTINGS_MODULE=stockscanner_django.settings_production
#   # Local defaults are read from your current .env/ENV (DB_*, DB2_*)
#   # Provide remote targets:
#   export REMOTE_DB_HOST=...
#   export REMOTE_DB_NAME=...
#   export REMOTE_DB_USER=...
#   export REMOTE_DB_PASSWORD=...
#   export REMOTE_DB_PORT=3306
#   export REMOTE_DB2_HOST=...
#   export REMOTE_DB2_NAME=...
#   export REMOTE_DB2_USER=...
#   export REMOTE_DB2_PASSWORD=...
#   export REMOTE_DB2_PORT=3306
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

  # Dump local default DB
  python manage.py dumpdata --database=default \
    --exclude=contenttypes --exclude=auth.permission --exclude=sessions.Session \
    --natural-foreign --natural-primary --indent 2 > /tmp/default_data.json

  # Dump local stocks DB (stocks + news apps)
  python manage.py dumpdata --database=stocks stocks news \
    --natural-foreign --natural-primary --indent 2 > /tmp/stocks_data.json

  # Load into remote by overriding DB_* and DB2_* in a subshell
  require_env REMOTE_DB_HOST; require_env REMOTE_DB_NAME; require_env REMOTE_DB_USER; require_env REMOTE_DB_PASSWORD
  require_env REMOTE_DB2_HOST; require_env REMOTE_DB2_NAME; require_env REMOTE_DB2_USER; require_env REMOTE_DB2_PASSWORD

  echo "Loading fixtures into remote default DB..."
  (
    export DB_HOST="$REMOTE_DB_HOST" DB_NAME="$REMOTE_DB_NAME" DB_USER="$REMOTE_DB_USER" DB_PASSWORD="$REMOTE_DB_PASSWORD" DB_PORT="${REMOTE_DB_PORT:-3306}"
    python manage.py loaddata --database=default /tmp/default_data.json --ignorenonexistent
  )

  echo "Loading fixtures into remote stocks DB..."
  (
    export DB2_HOST="$REMOTE_DB2_HOST" DB2_NAME="$REMOTE_DB2_NAME" DB2_USER="$REMOTE_DB2_USER" DB2_PASSWORD="$REMOTE_DB2_PASSWORD" DB2_PORT="${REMOTE_DB2_PORT:-3306}"
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

  # Require remote targets
  require_env REMOTE_DB_HOST; require_env REMOTE_DB_NAME; require_env REMOTE_DB_USER; require_env REMOTE_DB_PASSWORD
  require_env REMOTE_DB2_HOST; require_env REMOTE_DB2_NAME; require_env REMOTE_DB2_USER; require_env REMOTE_DB2_PASSWORD

  if have_cmd mysqldump && have_cmd mysql; then
    transfer_mysql_db "$LOCAL_DB_HOST" "$LOCAL_DB_NAME" "$LOCAL_DB_USER" "$LOCAL_DB_PASSWORD" "$LOCAL_DB_PORT" \
                      "$REMOTE_DB_HOST" "${REMOTE_DB_NAME}" "${REMOTE_DB_USER}" "${REMOTE_DB_PASSWORD}" "${REMOTE_DB_PORT:-3306}"

    transfer_mysql_db "$LOCAL_DB2_HOST" "$LOCAL_DB2_NAME" "$LOCAL_DB2_USER" "$LOCAL_DB2_PASSWORD" "$LOCAL_DB2_PORT" \
                      "$REMOTE_DB2_HOST" "${REMOTE_DB2_NAME}" "${REMOTE_DB2_USER}" "${REMOTE_DB2_PASSWORD}" "${REMOTE_DB2_PORT:-3306}"
  else
    transfer_via_django
  fi
}

main "$@"

