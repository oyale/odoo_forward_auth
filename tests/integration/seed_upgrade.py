"""Persist synthetic policy before an addon update in the disposable test DB."""
# Executed by `odoo shell`, which provides env. No production credentials.
group_field = "group_ids" if "group_ids" in env["res.users"]._fields else "groups_id"
group = env["res.groups"].create({"name": "Persisted Forward Auth Policy"})
user = env["res.users"].create({
    "name": "Upgrade Fixture",
    "login": "forward_auth_upgrade_fixture",
    "password": "integration-only",
    group_field: [(6, 0, [env.ref("base.group_user").id, group.id])],
})
for name, record in (("required_group", group), ("member", user)):
    env["ir.model.data"].create({
        "module": "forward_auth_upgrade_fixture",
        "name": name,
        "model": record._name,
        "res_id": record.id,
        "noupdate": True,
    })
env["ir.config_parameter"].sudo().set_param("odoo_forward_auth.group_id", group.id)
env.cr.commit()
