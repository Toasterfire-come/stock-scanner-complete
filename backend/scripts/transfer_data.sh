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

# Resolve a hostname to an IPv4 address using multiple methods
resolve_host_ip() {
  local host="$1"
  local ip=""

  # Allow manual override
  if [ -n "${REMOTE_DB_HOST_IP:-}" ]; then
    echo "$REMOTE_DB_HOST_IP"
    return 0
  fi

  # Prefer Python for accurate resolution when available
  if have_cmd python3; then
    ip=$(python3 - <<PY
import socket, sys
host = sys.argv[1]
try:
    print(socket.gethostbyname(host))
except Exception:
    pass
PY
"$host")
  fi
  if [ -z "$ip" ] && have_cmd python; then
    ip=$(python - <<PY
import socket, sys
host = sys.argv[1]
try:
    print(socket.gethostbyname(host))
except Exception:
    pass
PY
"$host")
  fi

  if [ -z "$ip" ] && have_cmd getent; then
    ip=$(getent hosts "$host" | awk '{print $1; exit}' || true)
  fi

  if have_cmd nslookup; then
    ip=$(nslookup "$host" 2>/dev/null | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | tail -n1 || true)
  fi
  if [ -z "$ip" ]; then
    # Try ping (Windows: -n 1, Unix: -c 1)
    if have_cmd ping; then
      ip=$(ping -n 1 "$host" 2>/dev/null | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -n1 || true)
      if [ -z "$ip" ]; then
        ip=$(ping -c 1 "$host" 2>/dev/null | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -n1 || true)
      fi
    fi
  fi
  if [ -z "$ip" ] && have_cmd curl; then
    # Try Google DoH
    ip=$(curl -s "https://dns.google/resolve?name=${host}&type=A" | grep -oE '\\"data\\":\\"([0-9]{1,3}\\.){3}[0-9]{1,3}\\"' | head -n1 | sed 's/.*\\"data\\":\\"\([^\\"]*\)\\".*/\1/' || true)
    if [ -z "$ip" ]; then
      # Try Cloudflare DoH
      ip=$(curl -s -H 'accept: application/dns-json' "https://cloudflare-dns.com/dns-query?name=${host}&type=A" | grep -oE '\\"data\\":\\"([0-9]{1,3}\\.){3}[0-9]{1,3}\\"' | head -n1 | sed 's/.*\\"data\\":\\"\([^\\"]*\)\\".*/\1/' || true)
    fi
  fi
  # Avoid returning DNS server IPs as bogus results
  if [ "$ip" = "1.1.1.1" ] || [ "$ip" = "8.8.8.8" ]; then
    ip=""
  fi
  echo "$ip"
}

# Optionally create an SSH tunnel through a jump host (e.g., your SFTP host)
setup_ssh_tunnel() {
  local remote_host="$1"
  local remote_port="$2"
  local ssh_host="${SSH_TUNNEL_HOST:-}"
  local ssh_user="${SSH_TUNNEL_USER:-}"
  local ssh_port="${SSH_TUNNEL_PORT:-22}"
  local local_port="${TUNNEL_LOCAL_PORT:-33306}"

  if [ -z "$ssh_host" ] || [ -z "$ssh_user" ]; then
    echo "SSH tunnel requested but SSH_TUNNEL_HOST/SSH_TUNNEL_USER not set; skipping tunnel."
    return 1
  fi
  if ! have_cmd ssh; then
    echo "ssh not available; cannot create tunnel."
    return 1
  fi

  local base_cmd=(ssh -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=no -p "$ssh_port" -f -N -L "${local_port}:${remote_host}:${remote_port}" "${ssh_user}@${ssh_host}")
  if [ -n "${SSH_TUNNEL_KEY:-}" ] && [ -f "$SSH_TUNNEL_KEY" ]; then
    base_cmd=(ssh -i "$SSH_TUNNEL_KEY" -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=no -p "$ssh_port" -f -N -L "${local_port}:${remote_host}:${remote_port}" "${ssh_user}@${ssh_host}")
  elif [ -n "${SSH_TUNNEL_PASSWORD:-}" ] && have_cmd sshpass; then
    base_cmd=(sshpass -p "$SSH_TUNNEL_PASSWORD" ssh -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=no -p "$ssh_port" -f -N -L "${local_port}:${remote_host}:${remote_port}" "${ssh_user}@${ssh_host}")
  fi

  echo "Establishing SSH tunnel on localhost:${local_port} -> ${remote_host}:${remote_port} via ${ssh_user}@${ssh_host}:${ssh_port}"
  if ! "${base_cmd[@]}"; then
    echo "Failed to establish SSH tunnel."
    return 1
  fi
  # Give it a moment
  sleep 1
  export TUNNEL_LOCAL_PORT="$local_port"
  return 0
}

transfer_mysql_db() {
  local local_host="$1" local_name="$2" local_user="$3" local_pass="$4" local_port="${5:-3306}"
  local remote_host="$6" remote_name="$7" remote_user="$8" remote_pass="$9" remote_port="${10:-3306}"

  echo "Transferring MySQL database '$local_name' -> '$remote_name'..."

  # Use env var for password to avoid exposing in process list
  MYSQL_PWD_LOCAL="$local_pass" MYSQL_PWD_REMOTE="$remote_pass"
  export MYSQL_PWD="$MYSQL_PWD_LOCAL"

  # Create dump
  local dump_dir="${DUMP_DIR:-backups}"
  mkdir -p "$dump_dir"
  local timestamp
  timestamp="$(date +%Y%m%d_%H%M%S)"
  DUMP_FILE="${dump_dir}/${local_name}_dump_${timestamp}.sql"
  local err_file="${dump_dir}/${local_name}_dump_${timestamp}.err"
  set +e
  mysqldump --single-transaction --quick --skip-lock-tables \
    -h "$local_host" -P "$local_port" -u "$local_user" "$local_name" > "$DUMP_FILE" 2>"$err_file"
  local dump_rc=$?
  set -e
  if [ $dump_rc -ne 0 ]; then
    if grep -qi "Unknown database" "$err_file"; then
      echo "Local database '$local_name' not found; skipping this DB. See $err_file."
      rm -f "$DUMP_FILE"
      return 0
    fi
    echo "mysqldump failed (exit $dump_rc). See $err_file. Skipping remote import; keeping any partial dump at $DUMP_FILE."
    return 0
  fi

  # Optionally skip remote import (export-only mode)
  if [ "${EXPORT_ONLY:-}" = "1" ] || [ "${EXPORT_ONLY:-}" = "true" ]; then
    echo "EXPORT_ONLY is set; wrote dump at $DUMP_FILE and skipped remote import."
    return 0
  fi

  # Determine how to reach remote: SSH tunnel, IP fallback, or hostname
  target_host="$remote_host"
  target_port="$remote_port"

  if [ "${USE_SSH_TUNNEL:-}" = "1" ] || [ "${USE_SSH_TUNNEL:-}" = "true" ]; then
    if setup_ssh_tunnel "$remote_host" "$remote_port"; then
      target_host="127.0.0.1"
      target_port="${TUNNEL_LOCAL_PORT}"
    fi
  fi

  if [ "$target_host" = "$remote_host" ]; then
    ip_fallback=$(resolve_host_ip "$remote_host")
    if [ -n "$ip_fallback" ]; then
      target_host="$ip_fallback"
      echo "Resolved $remote_host to $target_host via fallback DNS."
    else
      echo "Warning: could not resolve $remote_host; attempting direct connect anyway."
    fi
  fi

  # Import to remote (do not abort on error; keep dump for manual import)
  export MYSQL_PWD="$MYSQL_PWD_REMOTE"
  set +e
  mysql -h "$target_host" -P "$target_port" -u "$remote_user" "$remote_name" < "$DUMP_FILE"
  local import_rc=$?
  set -e
  if [ $import_rc -ne 0 ]; then
    echo "Remote import failed (exit $import_rc). Keeping dump at $DUMP_FILE for manual import (e.g., phpMyAdmin)."
    return 0
  fi

  echo "Transfer complete for '$local_name'. Imported to remote and kept dump at $DUMP_FILE."
}

transfer_via_django() {
  echo "mysqldump not available. Falling back to Django dumpdata/loaddata fixtures..."

  # Remote targets must be present via DB_* and DB2_*
  require_env DB_HOST; require_env DB_NAME; require_env DB_USER; require_env DB_PASSWORD
  require_env DB2_HOST; require_env DB2_NAME; require_env DB2_USER; require_env DB2_PASSWORD

  local dump_dir
  dump_dir="${DUMP_DIR:-backups}"
  mkdir -p "$dump_dir"

  # Dump LOCAL databases by overriding env to point Django to local sources
  echo "Dumping LOCAL default DB via Django..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB_HOST="$LOCAL_DB_HOST" DB_NAME="$LOCAL_DB_NAME" DB_USER="$LOCAL_DB_USER" DB_PASSWORD="$LOCAL_DB_PASSWORD" DB_PORT="$LOCAL_DB_PORT"
    # Ensure local stocks DB is configured
    export DB2_HOST="$LOCAL_DB2_HOST" DB2_NAME="$LOCAL_DB2_NAME" DB2_USER="$LOCAL_DB2_USER" DB2_PASSWORD="$LOCAL_DB2_PASSWORD" DB2_PORT="$LOCAL_DB2_PORT"
    python manage.py dumpdata --database=default \
      --exclude=contenttypes --exclude=auth.permission --exclude=sessions.Session \
      --natural-foreign --natural-primary --indent 2 > "$dump_dir/default_data.json"
  )

  echo "Dumping LOCAL stocks DB via Django (apps: stocks, news)..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB_HOST="$LOCAL_DB_HOST" DB_NAME="$LOCAL_DB_NAME" DB_USER="$LOCAL_DB_USER" DB_PASSWORD="$LOCAL_DB_PASSWORD" DB_PORT="$LOCAL_DB_PORT"
    export DB2_HOST="$LOCAL_DB2_HOST" DB2_NAME="$LOCAL_DB2_NAME" DB2_USER="$LOCAL_DB2_USER" DB2_PASSWORD="$LOCAL_DB2_PASSWORD" DB2_PORT="$LOCAL_DB2_PORT"
    python manage.py dumpdata --database=stocks stocks news \
      --natural-foreign --natural-primary --indent 2 > "$dump_dir/stocks_data.json"
  )

  # Optionally skip remote import
  if [ "${EXPORT_ONLY:-}" = "1" ] || [ "${EXPORT_ONLY:-}" = "true" ]; then
    echo "EXPORT_ONLY is set; wrote fixtures to $dump_dir and skipped remote import."
    return 0
  fi

  # Load into REMOTE by ensuring DB_* and DB2_* (already set) are used
  echo "Loading fixtures into REMOTE default DB..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB_HOST="$DB_HOST" DB_NAME="$DB_NAME" DB_USER="$DB_USER" DB_PASSWORD="$DB_PASSWORD" DB_PORT="${DB_PORT:-3306}"
    set +e
    python manage.py loaddata --database=default "$dump_dir/default_data.json" --ignorenonexistent
    if [ $? -ne 0 ]; then
      echo "Remote load (default) failed. You can import $dump_dir/default_data.json manually."
    fi
    set -e
  )

  echo "Loading fixtures into REMOTE stocks DB..."
  (
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-stockscanner_django.settings_production}"
    export DB2_HOST="$DB2_HOST" DB2_NAME="$DB2_NAME" DB2_USER="$DB2_USER" DB2_PASSWORD="$DB2_PASSWORD" DB2_PORT="${DB2_PORT:-3306}"
    set +e
    python manage.py loaddata --database=stocks "$dump_dir/stocks_data.json" --ignorenonexistent
    if [ $? -ne 0 ]; then
      echo "Remote load (stocks) failed. You can import $dump_dir/stocks_data.json manually."
    fi
    set -e
  )

  echo "Fixture-based transfer complete."
}

main() {
  load_local_env

  # Resolve LOCAL sources strictly from LOCAL_DB_* or sane localhost defaults
  LOCAL_DB_HOST="${LOCAL_DB_HOST:-127.0.0.1}"
  LOCAL_DB_NAME="${LOCAL_DB_NAME:-stockscanner}"
  LOCAL_DB_USER="${LOCAL_DB_USER:-root}"
  LOCAL_DB_PASSWORD="${LOCAL_DB_PASSWORD:-}"
  LOCAL_DB_PORT="${LOCAL_DB_PORT:-3306}"

  LOCAL_DB2_HOST="${LOCAL_DB2_HOST:-$LOCAL_DB_HOST}"
  LOCAL_DB2_NAME="${LOCAL_DB2_NAME:-stocks}"
  LOCAL_DB2_USER="${LOCAL_DB2_USER:-$LOCAL_DB_USER}"
  LOCAL_DB2_PASSWORD="${LOCAL_DB2_PASSWORD:-$LOCAL_DB_PASSWORD}"
  LOCAL_DB2_PORT="${LOCAL_DB2_PORT:-$LOCAL_DB_PORT}"

  # Remote targets come from DB_* and DB2_* in env/.env (already set)
  require_env DB_HOST; require_env DB_NAME; require_env DB_USER; require_env DB_PASSWORD
  require_env DB2_HOST; require_env DB2_NAME; require_env DB2_USER; require_env DB2_PASSWORD

  if have_cmd mysqldump && have_cmd mysql; then
    if [ "${SKIP_DEFAULT:-}" != "1" ] && [ "${SKIP_DEFAULT:-}" != "true" ]; then
      transfer_mysql_db "$LOCAL_DB_HOST" "$LOCAL_DB_NAME" "$LOCAL_DB_USER" "$LOCAL_DB_PASSWORD" "$LOCAL_DB_PORT" \
                        "$DB_HOST" "${DB_NAME}" "${DB_USER}" "${DB_PASSWORD}" "${DB_PORT:-3306}"
    else
      echo "Skipping default DB transfer due to SKIP_DEFAULT flag."
    fi

    if [ "${SKIP_STOCKS:-}" != "1" ] && [ "${SKIP_STOCKS:-}" != "true" ]; then
      transfer_mysql_db "$LOCAL_DB2_HOST" "$LOCAL_DB2_NAME" "$LOCAL_DB2_USER" "$LOCAL_DB2_PASSWORD" "$LOCAL_DB2_PORT" \
                        "$DB2_HOST" "${DB2_NAME}" "${DB2_USER}" "${DB2_PASSWORD}" "${DB2_PORT:-3306}"
    else
      echo "Skipping stocks DB transfer due to SKIP_STOCKS flag."
    fi
  else
    transfer_via_django
  fi
}

main "$@"

