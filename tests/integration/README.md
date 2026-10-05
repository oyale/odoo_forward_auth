# Odoo–Nginx integration tests

Run from the repository root with Docker and Docker Compose installed:

```sh
sh tests/integration/run.sh
FORWARD_AUTH_DEMO=1 sh tests/integration/run.sh
```

The runner creates a unique Compose project, installs the addon into a fresh
PostgreSQL database, runs its Odoo HTTP tests through a real Nginx proxy,
persists a synthetic policy, updates the addon in that same database, reruns
the tests to check preserved configuration and membership, and
removes the containers, network, and volumes on exit. It publishes no host ports.
Images are downloaded on the first run. The database and credentials are disposable.

The proxy configuration is generated from the shipped examples. Coverage includes:

- installation with and without demo data, including the example group;
- settings and user membership preserved across a same-series addon update;
- internal, portal, anonymous, and unauthorized users;
- malformed/deleted group configuration, logout, and membership revocation;
- stripping cookies, client credentials, and upgrade headers;
- method restrictions and inaccessible internal auth location;
- fail-closed behavior with an unreachable Odoo backend;
- authorization despite an inherited `satisfy any; allow all;` policy.

Native Odoo runs skip the proxy, demo-data, and update-preservation checks
unless their corresponding integration environment flags are enabled.
The integration harness forwards Odoo's test-cursor cookie along with the synthetic
session so HTTP requests use the test transaction. Never run this stack against a
production database. These checks do not certify an existing deployment's TLS,
application content safety, or capacity; validate those on the intended deployment.

CI runs both demo modes. Each mode must pass both installation and addon-update
phases; a missing phase fails the runner. Demo records are asserted explicitly,
because Odoo can continue loading after a demo-data error.

These are same-series installation/update checks, not a cross-major Odoo database
migration. To move an existing database between Odoo major versions, first use a
supported database migration process, then install/update the matching addon
branch and validate its saved access group and user permissions on a staging copy.
The branch names indicate addon compatibility, not a database migration service.
