# Nginx reference

## Requirements

The `ngx_http_auth_request_module` must be compiled in:

```bash
nginx -V 2>&1 | grep -- --with-http_auth_request_module
```

Most distribution packages include it; source builds may not.

## The authorization location

Define the Odoo upstream in the `http` context (the snippets below reference it):

```nginx
upstream odoo_forward_auth_backend {
    server 127.0.0.1:8069;
}
```

```nginx
location = /_forward_auth {
    internal;
    proxy_pass http://odoo_forward_auth_backend/odoo-forward-auth/auth;
    proxy_cache off;
    proxy_connect_timeout 3s;
    proxy_read_timeout 10s;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header Cookie $http_cookie;
    proxy_set_header Authorization "";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
}
```

- `internal` keeps the location callable only from `auth_request`.
- `proxy_pass_request_body off` + empty `Content-Length` mirror the official
  example: the decision needs no body.
- The original `Cookie` is what carries the Odoo session.
- `Authorization` is cleared so a client credential never reaches Odoo.

## The protected location

```nginx
location ^~ /app/ {
    satisfy all;
    auth_request /_forward_auth;
    proxy_cache off;
    limit_except GET HEAD { deny all; }
    proxy_pass http://127.0.0.1:8025;
    proxy_set_header Cookie "";
    proxy_set_header Authorization "";
    proxy_http_version 1.1;
    proxy_set_header Upgrade "";
    proxy_set_header Connection "";
}
```

- `limit_except GET HEAD { deny all; }` restricts HTTP methods. The upstream
  must enforce read-only behavior too: GET handlers can have side effects.
- `proxy_set_header Cookie "";` keeps the Odoo session out of the protected
  service.
- `proxy_set_header Authorization "";` keeps any client credential out of the
  protected service, matching the `security.md` rule.
- Strip the prefix by using a trailing slash on `proxy_pass` if the upstream does
  not expect it; keep the prefix if the upstream is configured to serve under it.

## WebSockets

The example disables upgrades explicitly. Only enable WebSockets after reviewing
application permissions and Origin validation. HTTP method restrictions apply
only to the handshake; subsequent messages can perform writes. Authorization is
not repeated for messages. See [revocation](security.md#connections-survive-revocation).

For an application that requires WebSockets, define this in the `http` context:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}
```

Then replace the empty Upgrade and Connection headers in the protected location
with `$http_upgrade` and `$connection_upgrade`, respectively.

## Login and denial behavior

Denials remain 401, including users already logged in without the required group.
Sign in at `/web/login`, then revisit the protected URL. Automatic login redirects
are deliberately omitted: the endpoint does not distinguish missing login from
missing permission, and an unescaped `$request_uri` corrupts nested query values.

## Deployment requirements

- Include both example files in their respective contexts. Use the same HTTPS
  hostname as Odoo, with the session cookie path covering the protected prefix.
- Configure Odoo database selection (`dbfilter`) for that hostname. In multi-worker
  or multi-instance installations, authorization requests must reach the same
  session store and database as login requests.
- Keep the service inaccessible except through the proxy. Review the complete
  vhost for alternative routes, nested locations, and inherited access rules.
  `satisfy all` ensures an inherited `satisfy any` cannot bypass authorization.
- Authorization and protected-response proxy caching are explicitly disabled.
  Review any CDN or other cache in front of Nginx as well.
- The example bounds authorization connection and read inactivity to 3s and 10s.
  Tune these against measured latency. Every protected request, including assets,
  consumes Odoo capacity; load-test representative concurrency and apply suitable
  edge rate limits. Do not use a shared cached authorization decision to reduce load.
- One configured group applies to all services using this database's endpoint.
  The upstream receives no user identity or Odoo record permissions.
