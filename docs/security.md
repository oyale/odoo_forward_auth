# Security

## What this is

A way to reuse the Odoo session as an identity source for a proxy decision. It
is not an authentication protocol and adds no factor (no MFA). The security of
the protected service is bounded by the security of Odoo sessions.

## Trust boundary

The decision is only as strong as the Odoo session cookie. Protect that cookie
(HTTPS, `Secure`/`HttpOnly`) and Odoo itself. This pattern does not compensate
for a weak Odoo login.

## Browser origin is a trust boundary

The example serves the protected application under the same origin as Odoo.
Only use it for applications trusted as highly as Odoo. JavaScript served under
`/app/` can make authenticated requests to Odoo and read their responses. An XSS
in that application can therefore act with the visiting user's Odoo permissions.
Stripping the upstream Cookie header and setting HttpOnly do not prevent this.
Review any rendering of external HTML, including inbox message previews.

For less-trusted applications, use a separate browser origin with an
origin-separated authentication flow (for example OIDC). Moving this snippet to
another hostname is insufficient: host-only Odoo cookies will not follow it.
Do not broaden the Odoo cookie domain as a substitute for that design.

## Unified denial

The endpoint returns `401` for every denial, so a caller cannot tell whether an
account is internal or merely lacks the group. Only the authorized case is
distinguishable (`204`), which any access check must reveal.

## Connections survive revocation

Authorization runs at the start of an HTTP request or WebSocket handshake.
Revocation does not terminate existing WebSockets, downloads, or HTTP streams.
`proxy_read_timeout` measures inactivity between reads, not total lifetime;
traffic or heartbeat frames can keep a connection alive indefinitely.

Where bounded revocation is required, enforce an absolute connection lifetime,
periodically reauthorize in the application, or terminate active connections
through an operational layer. The addon does not provide those mechanisms.

## Defense in depth for the upstream

- Bind the protected service to loopback so Nginx is the only entry point.
- Optionally keep the service's own credentials and inject them from a root-only
  Nginx include, so direct access to the port is unusable.
- Never forward the client's `Authorization` header to the upstream.

## Content sensitivity

Authorization controls *who* may read the service, not *what* it holds. An
authorized user sees everything the service contains. Do not grant the role
broadly, and be deliberate about what data reaches the protected service.

## Method and path control

The proxy restricts HTTP methods with `limit_except`; this alone does not ensure
read-only access. GET handlers can have side effects, and WebSocket messages are
not subject to HTTP method restrictions. Enforce read-only permissions in the
upstream application. Removing the restriction exposes other HTTP methods too.

## Fail closed

A down or erroring Odoo denies access. Verify this behavior in production:
stopping Odoo must not open the gate.
