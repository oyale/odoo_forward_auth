.. _odoo-forward-auth:

==================
Odoo Forward Auth
==================

Exposes ``GET /odoo-forward-auth/auth`` for an Nginx ``auth_request``
subrequest. The endpoint reads the caller's Odoo session and answers:

* ``204`` when the user is an internal user and belongs to the configured
  group;
* ``401`` in every other case, including when no group is configured.

Configuration
=============

Install the module, then open **Settings > General Settings > Forward Auth** and
pick the **Authorized group**. It is required: with no group, every request is denied.

Demo data
=========

Databases created with demo data also load an example group
**Forward Auth (example)** and a demo user (``demo.forward.auth``) that belongs to
it. Select that group in **Settings > General Settings > Forward Auth** to try the
flow end to end. The group is a reference only; production databases must define
and select their own group.

Nginx
=====

Point the internal authorization location at the endpoint and protect the
service prefix with ``auth_request``. See the repository ``examples/`` directory
and ``docs/nginx.md``.

Tests
=====

.. code-block:: bash

    odoo-bin -d <db> -i odoo_forward_auth --test-enable --stop-after-init
