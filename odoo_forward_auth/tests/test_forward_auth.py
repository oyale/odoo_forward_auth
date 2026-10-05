# Copyright 2026 odoo-forward-auth contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os
from urllib.parse import urlparse

from odoo.tests import common as odoo_tests_common
from odoo.tests.common import HttpCase, new_test_user, tagged

from odoo.addons.odoo_forward_auth.controllers.forward_auth import PARAM_GROUP


@tagged("post_install", "-at_install")
class TestForwardAuth(HttpCase):
    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        # Odoo 17+ blocks external HTTP in tests; allow the integration proxy.
        proxy_host = urlparse(os.environ.get("FORWARD_AUTH_PROXY_URL", "")).hostname
        if proxy_host and urlparse(r.url).hostname == proxy_host:
            return odoo_tests_common._super_send(s, r, **kw)
        return super()._request_handler(s, r, **kw)

    def test_anonymous_is_denied(self):
        response = self.url_open("/odoo-forward-auth/auth")
        self.assertEqual(response.status_code, 401)
        self.assertIn("no-store", response.headers["Cache-Control"])

    def _configure_group(self):
        group = self.env["res.groups"].create({"name": "Forward Auth Test"})
        self.env["ir.config_parameter"].sudo().set_param(PARAM_GROUP, group.id)
        return group

    def test_internal_user_without_required_group_is_denied(self):
        self._configure_group()
        new_test_user(
            self.env, login="fa_plain", password="test", groups="base.group_user"
        )
        self.authenticate("fa_plain", "test")
        response = self.url_open("/odoo-forward-auth/auth")
        self.assertEqual(response.status_code, 401)

    def test_internal_user_with_group_is_allowed(self):
        group = self._configure_group()
        member = new_test_user(
            self.env, login="fa_member", password="test", groups="base.group_user"
        )
        member.write({"groups_id": [(4, group.id)]})
        self.authenticate("fa_member", "test")
        response = self.url_open("/odoo-forward-auth/auth")
        self.assertEqual(response.status_code, 204)
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_non_internal_user_with_group_is_denied(self):
        group = self._configure_group()
        portal = new_test_user(
            self.env, login="fa_portal", password="test", groups="base.group_portal"
        )
        portal.write({"groups_id": [(4, group.id)]})
        self.authenticate("fa_portal", "test")
        response = self.url_open("/odoo-forward-auth/auth")
        self.assertEqual(response.status_code, 401)

    def test_internal_user_without_configured_group_is_denied(self):
        self.env["ir.config_parameter"].sudo().set_param(PARAM_GROUP, "")
        new_test_user(
            self.env, login="fa_any", password="test", groups="base.group_user"
        )
        self.authenticate("fa_any", "test")
        response = self.url_open("/odoo-forward-auth/auth")
        self.assertEqual(response.status_code, 401)

    def _authenticate_member(self):
        group = self._configure_group()
        user = new_test_user(
            self.env, login="fa_lifecycle", password="test", groups="base.group_user"
        )
        user.write({"groups_id": [(4, group.id)]})
        self.authenticate("fa_lifecycle", "test")
        return user, group

    def test_invalid_group_configuration_is_denied(self):
        self._authenticate_member()
        for value in ("invalid", "0", "-1"):
            self.env["ir.config_parameter"].sudo().set_param(PARAM_GROUP, value)
            self.assertEqual(self.url_open("/odoo-forward-auth/auth").status_code, 401)

    def test_deleted_group_is_denied(self):
        _, group = self._authenticate_member()
        group.unlink()
        self.assertEqual(self.url_open("/odoo-forward-auth/auth").status_code, 401)

    def test_membership_revocation(self):
        user, group = self._authenticate_member()
        self.assertEqual(self.url_open("/odoo-forward-auth/auth").status_code, 204)
        user.write({"groups_id": [(3, group.id)]})
        self.assertEqual(self.url_open("/odoo-forward-auth/auth").status_code, 401)

    def test_logout(self):
        self._authenticate_member()
        self.assertEqual(self.url_open("/odoo-forward-auth/auth").status_code, 204)
        self.url_open("/web/session/logout")
        self.assertEqual(self.url_open("/odoo-forward-auth/auth").status_code, 401)

    def test_settings_round_trip(self):
        group = self._configure_group()
        settings = self.env["res.config.settings"].create(
            {"odoo_forward_auth_group_id": group.id}
        )
        settings.set_values()
        values = self.env["res.config.settings"].default_get(
            ["odoo_forward_auth_group_id"]
        )
        self.assertEqual(values["odoo_forward_auth_group_id"], group.id)
        settings.odoo_forward_auth_group_id = False
        settings.set_values()
        self.assertFalse(self.env["ir.config_parameter"].sudo().get_param(PARAM_GROUP))

    def test_proxy_contract(self):
        proxy = os.environ.get("FORWARD_AUTH_PROXY_URL")
        if not proxy:
            self.skipTest("Run tests/integration/run.sh for real Nginx coverage")
        self.assertEqual(self.url_open(proxy + "/app/").status_code, 401)
        user, group = self._authenticate_member()
        # Include the test-cursor cookie so proxy requests share this transaction.
        cookie = "; ".join(
            f"{key}={value}" for key, value in self.opener.cookies.items()
        )
        headers = {"Cookie": cookie, "Authorization": "Bearer synthetic"}
        response = self.url_open(proxy + "/app/", headers=headers)
        self.assertEqual(response.status_code, 200)
        echoed = {key.lower(): value for key, value in response.json().items()}
        self.assertNotIn("cookie", echoed)
        self.assertNotIn("authorization", echoed)
        upgraded = self.url_open(
            proxy + "/app/",
            headers={**headers, "Upgrade": "websocket", "Connection": "Upgrade"},
        )
        self.assertEqual(upgraded.status_code, 200)
        self.assertNotIn("upgrade", {key.lower() for key in upgraded.json()})
        self.assertEqual(
            self.url_open(proxy + "/app/", data="write", headers=headers).status_code,
            403,
        )
        self.assertEqual(
            self.url_open(proxy + "/_forward_auth", headers=headers).status_code, 404
        )
        self.assertEqual(self.url_open(proxy + ":8081/app/", headers=headers).status_code, 500)
        user.write({"groups_id": [(3, group.id)]})
        self.assertEqual(self.url_open(proxy + "/app/", headers=headers).status_code, 401)
