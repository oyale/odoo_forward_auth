# odoo-forward-auth

Use your existing **Odoo session** to gate any internal HTTP service behind an
Nginx `auth_request` check. Odoo answers a per-request authorization subrequest;
Nginx proxies or denies. No OIDC, no SAML, no change to the protected service.

> This is *not* real SSO. It reuses Odoo's session as the source of identity and
> adds no authentication factor. If you already run an OIDC/SAML provider, use
> that instead. See [docs/security.md](docs/security.md).

Use this only for applications trusted as highly as Odoo: the example shares
Odoo's browser origin, so an XSS in the protected application can act as the
visiting Odoo user. See the [trust boundary](docs/security.md#browser-origin-is-a-trust-boundary).

## How it works

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Nginx
    participant O as Odoo
    participant S as Protected service
    B->>N: GET /app/ (session_id cookie)
    N->>O: internal subrequest GET /odoo-forward-auth/auth (Cookie)
    O-->>N: 204 allow / 401 deny
    alt 204
        N->>S: proxy GET /app/
        S-->>B: response
    else 401
        N-->>B: 401
    end
```

1. The browser requests a path under the protected prefix, sending its Odoo
   `session_id` cookie.
2. Nginx sends an **internal** subrequest to the Odoo authorization endpoint,
   forwarding the cookie and stripping the body.
3. Odoo loads the session and checks the "internal user" condition and
   membership of the configured group. It answers `204` or `401`; with no group
   configured, every request is denied.
4. On `204` only, Nginx proxies the original request to the protected upstream.

## Repository layout

- `odoo_forward_auth/` — installable Odoo 16 addon with the authorization route.
- `examples/` — annotated Nginx configuration.
- `docs/` — [how it works](docs/how-it-works.md),
  [Nginx reference](docs/nginx.md),
  [security](docs/security.md).

## Quickstart

1. Install the addon and set the authorized group in
   **Settings > General Settings > Forward Auth**.
2. Add `examples/nginx-forward-auth-http.conf` in Nginx's `http` context and
   `examples/nginx-forward-auth.conf` inside your Odoo `server` block, adjusting
   the upstreams and prefix. Review the [deployment requirements](docs/nginx.md#deployment-requirements).
3. `nginx -t && systemctl reload nginx`.
4. Visit the protected prefix with an Odoo session that belongs to the group.

## Compatibility

This repository ships one branch per Odoo series. Check out the branch that
matches your Odoo version:

| Branch | Odoo | Integration tests |
|--------|------|-------------------|
| [`16.0`](https://github.com/oyale/odoo_forward_auth/tree/16.0) | 16.0 | [![Integration 16.0](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml/badge.svg?branch=16.0&event=push)](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml?query=branch%3A16.0+event%3Apush) |
| [`17.0`](https://github.com/oyale/odoo_forward_auth/tree/17.0) | 17.0 | [![Integration 17.0](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml/badge.svg?branch=17.0&event=push)](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml?query=branch%3A17.0+event%3Apush) |
| [`18.0`](https://github.com/oyale/odoo_forward_auth/tree/18.0) | 18.0 | [![Integration 18.0](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml/badge.svg?branch=18.0&event=push)](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml?query=branch%3A18.0+event%3Apush) |
| [`19.0`](https://github.com/oyale/odoo_forward_auth/tree/19.0) | 19.0 | [![Integration 19.0](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml/badge.svg?branch=19.0&event=push)](https://github.com/oyale/odoo_forward_auth/actions/workflows/integration.yml?query=branch%3A19.0+event%3Apush) |

`main` mirrors `16.0` and is kept as the default branch. The settings-view
extension differs between series, so use the branch that matches your Odoo
version. The `19.0` branch also renames the user group field (`groups_id` →
`group_ids`).

## Tests

Run `sh tests/integration/run.sh` with Docker and Docker Compose installed.
The [integration harness](tests/integration/README.md) installs the addon into a
fresh database and checks the shipped proxy configuration. CI runs the same command.

## License

AGPL-3.0. See [LICENSE](LICENSE).
