# Nginx example

`nginx-forward-auth.conf` is a copy-paste starting point. Replace:

- `127.0.0.1:8069` with your Odoo upstream;
- `/app/` with the prefix of the service you are protecting;
- `127.0.0.1:8025` with your service's upstream;
- optionally uncomment the `error_page` block to redirect to the Odoo login.

Notes:

- The `/_forward_auth` location is `internal`; clients cannot call it directly.
- `auth_request` fails **closed**: any non-2xx answer from Odoo denies access.
- The authorization answer is not cached; group changes apply on the next request.
- `limit_except GET HEAD { deny all; }` is what makes the access read-only. It is
  not enforced by the Odoo addon.
