#!/bin/sh
set -eu
cd "$(dirname "$0")"
# Unique project avoids touching any existing stack; no host ports are exposed.
project="forward-auth-test-$$"
case "${FORWARD_AUTH_DEMO:-0}" in
    0|1) ;;
    *) echo 'FORWARD_AUTH_DEMO must be 0 or 1' >&2; exit 2 ;;
esac
if docker compose version >/dev/null 2>&1; then
    compose() { docker compose "$@"; }
else
    compose() { docker-compose "$@"; }
fi
cleanup() { compose -p "$project" -f compose.yaml down -v --remove-orphans; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
compose -p "$project" -f compose.yaml up --abort-on-container-exit --exit-code-from odoo
# Compose can return zero when a dependency exits before Odoo starts.
# Require both validated phases as well as the container exit status.
if ! compose -p "$project" -f compose.yaml logs odoo | grep -q FORWARD_AUTH_INSTALL_AND_UPDATE_PASSED; then
    echo 'Odoo did not complete both installation and update checks' >&2
    exit 1
fi
