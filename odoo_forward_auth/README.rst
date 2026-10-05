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

Nginx
=====

Point the internal authorization location at the endpoint and protect the
service prefix with ``auth_request``. See the repository ``examples/`` directory
and ``docs/nginx.md``.

Tests
=====

.. code-block:: bash

    odoo-bin -d <db> -i odoo_forward_auth --test-enable --stop-after-init
