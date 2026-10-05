# Contributing

Thanks for improving `odoo-forward-auth`.

## License

By contributing you agree your contribution is licensed under the
**GNU Affero General Public License v3.0** (see `LICENSE`). Sign off commits
with `git commit -s`.

## How to propose a change

1. Open an issue describing the problem and the Odoo/Nginx versions involved.
2. Keep the addon's contract intact: allow = `204`, denial = `401`, no method
   or path filtering inside Odoo.
3. Update the relevant document under `docs/` and the Nginx example if the
   request lifecycle changes.
4. Run `sh tests/integration/run.sh` and
   `FORWARD_AUTH_DEMO=1 sh tests/integration/run.sh` before submitting. This installs the addon
   in a disposable database and tests the shipped Nginx examples; see
   [the integration guide](tests/integration/README.md). Native Odoo test
   instructions remain available in `odoo_forward_auth/README.rst`, but skip
   environment-specific checks unless the integration environment is configured.
