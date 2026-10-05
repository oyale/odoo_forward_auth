# Odoo–Nginx integration tests

Run from the repository root with Docker and Docker Compose installed:

```sh
sh tests/integration/run.sh
```

The runner creates a unique Compose project, installs the addon into a fresh
PostgreSQL database, runs its Odoo HTTP tests through a real Nginx proxy, and
removes the containers, network, and volumes on exit. It publishes no host ports.
Images are downloaded on the first run. The database and credentials are disposable.

The proxy configuration is generated from the shipped examples. Coverage includes:

- installation and settings persistence;
- internal, portal, anonymous, and unauthorized users;
- malformed/deleted group configuration, logout, and membership revocation;
- stripping cookies, client credentials, and upgrade headers;
- method restrictions and inaccessible internal auth location;
- fail-closed behavior with an unreachable Odoo backend;
- authorization despite an inherited `satisfy any; allow all;` policy.

Without `FORWARD_AUTH_PROXY_URL`, native Odoo tests skip only the proxy test.
The integration harness forwards Odoo's test-cursor cookie along with the synthetic
session so HTTP requests use the test transaction. Never run this stack against a
production database. These checks do not certify an existing deployment's TLS,
application content safety, or capacity; validate those on the intended deployment.
