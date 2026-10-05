# Copyright 2026 odoo-forward-auth contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request

PARAM_GROUP = "odoo_forward_auth.group_id"


class ForwardAuth(http.Controller):
    @http.route(
        "/odoo-forward-auth/auth",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
        save_session=False,
    )
    def authorize(self):
        response = request.make_response("")
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"

        user = request.env.user
        group = self._required_group()
        allowed = (
            user.has_group("base.group_user")
            and group is not None
            and group in user.all_group_ids
        )
        response.status_code = 204 if allowed else 401
        return response

    def _required_group(self):
        value = request.env["ir.config_parameter"].sudo().get_param(PARAM_GROUP)
        if not value:
            return None
        try:
            group_id = int(value)
        except (TypeError, ValueError):
            return None
        group = request.env["res.groups"].sudo().browse(group_id).exists()
        return group or None
