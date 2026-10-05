# Nginx reference

## Requirements

The `ngx_http_auth_request_module` must be compiled in:

```bash
nginx -V 2>&1 | grep -- --with-http_auth_request_module
```

Most distribution packages include it; source builds may not.

## The authorization location

```nginx
location = /_forward_auth {
    internal;
    proxy_pass http://odoo/odoo-forward-auth/auth;
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
    auth_request /_forward_auth;
    limit_except GET HEAD { deny all; }
    proxy_pass http://127.0.0.1:8025;
    proxy_set_header Cookie "";
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
}
```

- `limit_except GET HEAD { deny all; }` is the read-only switch. Put
  authorization in Odoo, method restrictions in Nginx.
- `proxy_set_header Cookie "";` keeps the Odoo session out of the protected
  service.
- Strip the prefix by using a trailing slash on `proxy_pass` if the upstream does
  not expect it; keep the prefix if the upstream is configured to serve under it.

## WebSockets

`auth_request` runs on the upgrade handshake. Pass `Upgrade` and `Connection`
explicitly and use HTTP/1.1; Nginx does not forward hop-by-hop headers by
default.

## Optional: redirect to the Odoo login

```nginx
error_page 401 = @odoo_login;
location @odoo_login {
    return 302 https://$host/web/login?redirect=$request_uri;
}
```

This changes the UX only. The authorization decision is unchanged.
