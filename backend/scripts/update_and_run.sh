#!/usr/bin/env bash
set -euo pipefail

# update_and_run.sh
# One-shot script to update Django settings, configure Cloudflare Tunnel to 127.0.0.1, 
# start Django + tunnel, and verify public /health/. Optionally updates WordPress backend URL.

# Defaults (override with flags)
CF_HOST="api.retailtradescanner.com"
TUNNEL_UUID="66a404f0-c651-4141-bb4e-008a551bc5b5"
PROJECT_DIR="$(pwd)"
DJANGO_HOST="127.0.0.1"
DJANGO_PORT="8000"
RUN_MIGRATIONS=0
UPDATE_GIT=1
UPDATE_WP=0
WP_CLI_CMD="wp"

# Helpers
log() { echo -e "[INFO] $*"; }
warn() { echo -e "[WARN] $*" >&2; }
err() { echo -e "[ERROR] $*" >&2; }
exists() { command -v "$1" >/dev/null 2>&1; }

die() { err "$*"; exit 1; }

usage() {
	cat <<EOF
Usage: $0 [--host CF_HOST] [--tunnel UUID] [--project PATH] [--no-pull] [--migrate] [--update-wp]

Options:
  --host CF_HOST       Cloudflare hostname (default: ${CF_HOST})
  --tunnel UUID        Cloudflare Tunnel UUID (default: ${TUNNEL_UUID})
  --project PATH       Project root (default: current directory)
  --no-pull            Skip git pull from main
  --migrate            Run Django migrations before start
  --update-wp          Update WordPress backend_url option to CF_HOST (requires wp-cli in PATH)
  -h, --help           Show this help
EOF
}

# Parse args
while [[ $# -gt 0 ]]; do
	case "$1" in
		--host) CF_HOST="$2"; shift 2;;
		--tunnel) TUNNEL_UUID="$2"; shift 2;;
		--project) PROJECT_DIR="$2"; shift 2;;
		--no-pull) UPDATE_GIT=0; shift;;
		--migrate) RUN_MIGRATIONS=1; shift;;
		--update-wp) UPDATE_WP=1; shift;;
		-h|--help) usage; exit 0;;
		*) err "Unknown arg: $1"; usage; exit 1;;
	esac
done

cd "$PROJECT_DIR" || die "Project directory not found: $PROJECT_DIR"

# 0) Sanity checks
for cmd in curl cloudflared; do
	exists "$cmd" || die "Required command not found: $cmd"
done

# Git optional
if [[ $UPDATE_GIT -eq 1 ]] && exists git; then
	log "Pulling latest main..."
	git fetch origin || warn "git fetch failed (continuing)"
	if git rev-parse --verify main >/dev/null 2>&1; then
		git checkout main || warn "git checkout main failed (continuing)"
		git pull --rebase origin main || warn "git pull failed (continuing)"
	fi
else
	log "Skipping git pull"
fi

# 1) Ensure .env contains ALLOWED_HOSTS that includes CF_HOST
ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
	log "Creating .env"
	touch "$ENV_FILE"
fi
# Compose ALLOWED_HOSTS
DEFAULT_HOSTS="localhost,127.0.0.1,${CF_HOST}"
if grep -q '^ALLOWED_HOSTS=' "$ENV_FILE"; then
	# Merge CF_HOST if missing
	current=$(grep '^ALLOWED_HOSTS=' "$ENV_FILE" | cut -d'=' -f2)
	IFS=',' read -r -a arr <<<"$current"
	found=0
	for h in "${arr[@]}"; do [[ "$h" == "$CF_HOST" ]] && found=1; done
	if [[ $found -eq 0 ]]; then
		new_hosts="${current},${CF_HOST}"
		sed -i.bak "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=${new_hosts}/" "$ENV_FILE"
		log "Updated ALLOWED_HOSTS=${new_hosts} in .env"
	else
		log ".env ALLOWED_HOSTS already includes ${CF_HOST}"
	fi
else
	echo "ALLOWED_HOSTS=${DEFAULT_HOSTS}" >> "$ENV_FILE"
	log "Wrote ALLOWED_HOSTS=${DEFAULT_HOSTS} to .env"
fi

# 2) Ensure Django settings trust CF host and proxy SSL header
SETTINGS_PY="stockscanner_django/settings.py"
[[ -f "$SETTINGS_PY" ]] || die "Django settings not found: $SETTINGS_PY"

grep -q '^CSRF_TRUSTED_ORIGINS' "$SETTINGS_PY" || {
	echo "CSRF_TRUSTED_ORIGINS = [\"https://${CF_HOST}\"]" >> "$SETTINGS_PY"
	log "Appended CSRF_TRUSTED_ORIGINS to settings.py"
}

grep -q '^SECURE_PROXY_SSL_HEADER' "$SETTINGS_PY" || {
	echo 'SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")' >> "$SETTINGS_PY"
	log "Appended SECURE_PROXY_SSL_HEADER to settings.py"
}

# 3) Optional: migrations
PY_CMD="python3"
exists py && PY_CMD="py -3"

if [[ $RUN_MIGRATIONS -eq 1 ]]; then
	log "Running migrations..."
	$PY_CMD manage.py migrate || warn "Migrations failed"
fi

# 4) Start Django on 127.0.0.1:8000 (background)
log "Starting Django (${DJANGO_HOST}:${DJANGO_PORT})..."
$PY_CMD manage.py runserver ${DJANGO_HOST}:${DJANGO_PORT} >/dev/null 2>&1 &
DJANGO_PID=$!
sleep 2
if ps -p $DJANGO_PID >/dev/null 2>&1; then
	log "Django started (PID ${DJANGO_PID})"
else
	warn "Django may not have started (PID ${DJANGO_PID})"
fi

# 5) Write cloudflared config to use 127.0.0.1 (avoid ::1)
CLOUDFLARED_DIR="${USERPROFILE:-$HOME}/.cloudflared"
mkdir -p "$CLOUDFLARED_DIR"
CONFIG_YML="$CLOUDFLARED_DIR/config.yml"
cat > "$CONFIG_YML" <<YAML
tunnel: ${TUNNEL_UUID}
credentials-file: ${CLOUDFLARED_DIR//\\//}/${TUNNEL_UUID}.json
ingress:
  - hostname: ${CF_HOST}
    service: http://${DJANGO_HOST}:${DJANGO_PORT}
  - service: http_status:404
YAML
log "Wrote cloudflared config: $CONFIG_YML"

# 6) Check creds file
CREDS_JSON="${CLOUDFLARED_DIR}/${TUNNEL_UUID}.json"
if [[ ! -f "$CREDS_JSON" ]]; then
	warn "Credentials file not found: $CREDS_JSON"
	warn "Run: cloudflared login && cloudflared tunnel token ${TUNNEL_UUID}"
fi

# 7) Start cloudflared (background)
log "Starting Cloudflare Tunnel for ${CF_HOST} -> http://${DJANGO_HOST}:${DJANGO_PORT}..."
cloudflared tunnel --config "$CONFIG_YML" run "$TUNNEL_UUID" >/dev/null 2>&1 &
CF_PID=$!
sleep 4
if ps -p $CF_PID >/dev/null 2>&1; then
	log "Cloudflared started (PID ${CF_PID})"
else
	warn "Cloudflared may not have started (PID ${CF_PID}). Check logs by running without redirection."
fi

# 8) Verify local health
if curl -fsS "http://${DJANGO_HOST}:${DJANGO_PORT}/health/" >/dev/null; then
	log "Local Django health OK"
else
	warn "Local Django health FAILED at http://${DJANGO_HOST}:${DJANGO_PORT}/health/"
fi

# 9) Verify public health (retry)
ATTEMPTS=12
SLEEP=5
ok=0
for i in $(seq 1 $ATTEMPTS); do
	if curl -fsS "https://${CF_HOST}/health/" >/dev/null; then
		log "Public health OK at https://${CF_HOST}/health/"
		ok=1; break
	else
		warn "Public health not ready yet (attempt $i/${ATTEMPTS})..."
		sleep $SLEEP
	fi

done

if [[ $ok -eq 0 ]]; then
	warn "Public health check failed. Ensure Zero Trust hostname points to http://${DJANGO_HOST}:${DJANGO_PORT} and creds exist: $CREDS_JSON"
fi

# 10) Optional: Update WordPress backend URL if wp-cli exists
if [[ $UPDATE_WP -eq 1 ]]; then
	if exists "$WP_CLI_CMD"; then
		log "Updating WordPress backend_url to https://${CF_HOST} (requires correct WP path & permissions)"
		set +e
		$WP_CLI_CMD option update stock_scanner_api_settings "{\"backend_url\":\"https://${CF_HOST}\",\"api_key\":\"\",\"timeout\":30}" --format=json
		set -e
	else
		warn "wp-cli not found; skipping WordPress option update"
	fi
fi

log "Done. Django PID=${DJANGO_PID}, Cloudflared PID=${CF_PID}"
log "Test manually: curl -sI https://${CF_HOST}/health/ | head -n1"