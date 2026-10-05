{
    "name": "Odoo Forward Auth",
    "summary": "Authorization endpoint for Nginx auth_request using the Odoo session.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "odoo-forward-auth contributors",
    "website": "https://github.com/odoo-forward-auth/odoo-forward-auth",
    "category": "Hidden/Tools",
    "depends": ["base"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
