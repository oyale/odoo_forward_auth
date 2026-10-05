# Copyright 2026 odoo-forward-auth contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    odoo_forward_auth_group_id = fields.Many2one(
        "res.groups",
        string="Required Group",
        config_parameter="odoo_forward_auth.group_id",
        help="Group a user must belong to. Required: with no group, every request is denied.",
    )
