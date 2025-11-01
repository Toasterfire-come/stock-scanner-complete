#!/bin/sh
set -eu

# Ensure required tools are available
for cmd in sshpass ssh tar; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$cmd" >&2
    exit 1
  fi
done

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

# Adjust these via environment variables when invoking the script.
REPO_ROOT_REL=${REPO_ROOT_REL:-.}
BUILD_WORKDIR_REL=${BUILD_WORKDIR_REL:-frontend}
BUILD_OUTPUT_REL=${BUILD_OUTPUT_REL:-build}
BUILD_CMD=${BUILD_CMD:-"npm run build"}

REMOTE_HOSTNAME=${REMOTE_HOSTNAME:-access-5018544625.webspace-host.com}
REMOTE_PORT=${REMOTE_PORT:-22}
REMOTE_USER=${REMOTE_USER:-a1531117}
REMOTE_ROOT=${REMOTE_ROOT:-.}
KEEP_REMOTE_ITEMS=${KEEP_REMOTE_ITEMS:-".ssh"}
SSH_OPTS=${SSH_OPTS:-"-o StrictHostKeyChecking=accept-new"}

if [ "${SFTP_PASSWORD:-}" = "" ]; then
  printf 'Set SFTP_PASSWORD environment variable before running this script.\n' >&2
  exit 1
fi

REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/$REPO_ROOT_REL" && pwd -P)
BUILD_WORKDIR="$REPO_ROOT/$BUILD_WORKDIR_REL"
BUILD_OUTPUT="$BUILD_WORKDIR/$BUILD_OUTPUT_REL"

printf 'Repository root      : %s\n' "$REPO_ROOT"
printf 'Build working dir    : %s\n' "$BUILD_WORKDIR"
printf 'Build output dir     : %s\n' "$BUILD_OUTPUT"
printf 'Remote destination   : %s@%s:%s (path: %s)\n' \
  "$REMOTE_USER" "$REMOTE_HOSTNAME" "$REMOTE_PORT" "$REMOTE_ROOT"
printf 'Keeping remote items : %s\n' "$KEEP_REMOTE_ITEMS"

if [ ! -d "$BUILD_WORKDIR" ]; then
  printf 'Build working directory not found: %s\n' "$BUILD_WORKDIR" >&2
  exit 1
fi

printf 'Running build command: %s\n' "$BUILD_CMD"
(
  cd "$BUILD_WORKDIR"
  sh -c "$BUILD_CMD"
)

if [ ! -d "$BUILD_OUTPUT" ]; then
  printf 'Build output directory not found after build: %s\n' "$BUILD_OUTPUT" >&2
  exit 1
fi

printf 'Cleaning remote path...\n'
sshpass -p "$SFTP_PASSWORD" \
  ssh $SSH_OPTS -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOSTNAME" 'sh -s' "$REMOTE_ROOT" "$KEEP_REMOTE_ITEMS" <<'REMOTE_SH'
set -eu
REMOTE_ROOT=$1
KEEP_ITEMS=$2

mkdir -p "$REMOTE_ROOT"
cd "$REMOTE_ROOT"

keep_match() {
  target=$1
  for keep in $KEEP_ITEMS; do
    if [ "$target" = "$keep" ]; then
      return 0
    fi
  done
  return 1
}

for entry in ./* ./.??*; do
  if [ ! -e "$entry" ]; then
    continue
  fi
  name=${entry#./}
  if [ "$name" = "." ] || [ "$name" = ".." ]; then
    continue
  fi
  if keep_match "$name"; then
    continue
  fi
  if [ -d "$entry" ]; then
    chmod -R u+w "$entry" 2>/dev/null || true
    rm -rf "$entry"
  else
    chmod u+w "$entry" 2>/dev/null || true
    rm -f "$entry"
  fi
done
REMOTE_SH

printf 'Uploading new build artifacts...\n'
tar -C "$BUILD_OUTPUT" -cf - . \
  | sshpass -p "$SFTP_PASSWORD" \
    ssh $SSH_OPTS -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOSTNAME" 'sh -s' "$REMOTE_ROOT" <<'REMOTE_SH'
set -eu
REMOTE_ROOT=$1

mkdir -p "$REMOTE_ROOT"
cd "$REMOTE_ROOT"
tar -xf -
REMOTE_SH

printf 'Deployment complete.\n'
