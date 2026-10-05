#!/bin/bash
set -euo pipefail
# The official image entrypoint supplies database connection arguments.
demo_args=(--without-demo=all)
if [ "${FORWARD_AUTH_DEMO:-0}" = 1 ]; then
    demo_args=()
fi
common=(-d forward_auth_test --http-interface=0.0.0.0 '--db-filter=^forward_auth_test$')
run_tests() {
    /entrypoint.sh odoo "${common[@]}" "${demo_args[@]}" "$1" odoo_forward_auth \
        --test-enable --test-tags=/odoo_forward_auth --stop-after-init 2>&1 | tee /tmp/phase.log
    grep -Eq '0 failed, 0 error.* of [1-9][0-9]* tests' /tmp/phase.log
}
run_tests -i
/entrypoint.sh odoo shell -d forward_auth_test --no-http < /tests/seed_upgrade.py
export FORWARD_AUTH_UPGRADE_CHECK=1
run_tests -u
echo FORWARD_AUTH_INSTALL_AND_UPDATE_PASSED
