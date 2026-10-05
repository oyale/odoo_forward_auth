from odoo.tests.common import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestForwardAuth(HttpCase):
    def test_anonymous_is_denied(self):
        response = self.url_open("/odoo-forward-auth/auth")
        self.assertEqual(response.status_code, 401)

    def _configure_group(self):
        group = self.env["res.groups"].create({"name": "Forward Auth Test"})
        self.env["ir.config_parameter"].sudo().set_param(
            "odoo_forward_auth.group_id", group.id
        )
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

    def test_internal_user_without_configured_group_is_denied(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "odoo_forward_auth.group_id", ""
        )
        new_test_user(
            self.env, login="fa_any", password="test", groups="base.group_user"
        )
        self.authenticate("fa_any", "test")
        response = self.url_open("/odoo-forward-auth/auth")
        self.assertEqual(response.status_code, 401)
