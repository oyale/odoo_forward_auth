#!/bin/sh
set -eu
cd "$(dirname "$0")"
# Unique project avoids touching any existing stack; no host ports are exposed.
project="forward-auth-test-$$"
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
# Require Odoo's successful test summary as well as the container exit status.
if ! compose -p "$project" -f compose.yaml logs odoo | grep -Eq '0 failed, 0 error.* of [1-9][0-9]* tests'; then
    echo 'Odoo did not report a successful test run' >&2
    exit 1
fi
