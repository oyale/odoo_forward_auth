#!/bin/sh
set -eu
# Exercise the shipped snippets, including inheritance from an unsafe parent.
sed 's/127.0.0.1:8069/odoo:8069/' /examples/nginx-forward-auth-http.conf > /tmp/http.conf
sed 's/127.0.0.1:8025/upstream:8025/' /examples/nginx-forward-auth.conf > /tmp/server.conf
sed -e 's@http://odoo_forward_auth_backend/odoo-forward-auth/auth@http://127.0.0.1:1/odoo-forward-auth/auth@' /tmp/server.conf > /tmp/broken.conf
cat > /etc/nginx/nginx.conf <<'NGINX'
events {}
http {
    include /tmp/http.conf;
    server {
        listen 80;
        satisfy any;
        allow all;
        include /tmp/server.conf;
    }
    server {
        listen 8081;
        include /tmp/broken.conf;
    }
}
NGINX
nginx -t
exec nginx -g 'daemon off;'
