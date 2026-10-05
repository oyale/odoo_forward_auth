# How it works

## The subrequest

Nginx `auth_request` performs an internal subrequest before serving the real
request. Nginx allows the request only when the subrequest returns a 2xx status;
`401` and `403` deny it, and any other status is treated as an authorization
error. The addon therefore answers exactly `204` (allow) or `401` (deny).

## Why a dedicated HTTP route

The subrequest must reflect the caller's *existing* session. Odoo stores the
session id in the `session_id` cookie and loads the user from it on every
request, so a plain `type="http"` route with `auth="public"` can inspect the
current `request.env.user` without asking for credentials again.

A JSON-RPC endpoint is a poor fit: it cannot express a bare 204/401 cleanly, and
its response envelope is not a status code. A login route is worse: it consumes
credentials and validates nothing about an existing session.

## Why the route path is fixed

Odoo registers routes at import time from the `@http.route` decorator. The path
cannot be changed at runtime from a setting. Only the required group is a
setting. This is intentional: one stable, documented endpoint is easier to wire
and audit than a dynamic one.

## Internal user and group

The endpoint allows a request when the user belongs to `base.group_user`
(internal) and is a member of the configured group. The group is mandatory: if
none is configured, every request is denied. The public user is never internal,
so anonymous requests always fail.

## Fail closed

If Odoo is down or returns an error, the subrequest is not 2xx and Nginx denies
access. A redirect is also not 2xx and is therefore denied; do not point the
authorization location at a login route.

## Caching

The authorization answer is per request and is not cached. Removing a user from
the group takes effect on the next request. Existing WebSockets, downloads, and HTTP streams continue; see [security.md](security.md).
