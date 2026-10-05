.. _odoo-forward-auth:

==================
Odoo Forward Auth
==================

Exposes ``GET /odoo-forward-auth/auth`` for an Nginx ``auth_request``
subrequest. The endpoint reads the caller's Odoo session and answers:

* ``204`` when the user is an internal user and belongs to the configured
  group;
* ``401`` in every other case, including when no group is configured.

Compatibility
=============

Built and tested on **Odoo 16.0 only**. Other versions are untested.

Configuration
=============

Install the module, then open **Settings > General Settings > Forward Auth** and
pick the **Authorized group**. It is required: with no group, every request is denied.

Demo data
=========

Databases created with demo data load only the example group
**Forward Auth (example)**. Create a local test user with a unique password and
assign the group explicitly to try the flow. No demonstration login is created.
Production databases must define and select their own group.

When upgrading a database that loaded an older version's demo data, archive the
existing ``demo.forward.auth`` user and invalidate its sessions. Removing the XML
record does not remove an existing ``noupdate`` account during an upgrade.

Nginx
=====

Point the internal authorization location at the endpoint and protect the
service prefix with ``auth_request``. See the repository ``examples/`` directory
and ``docs/nginx.md``.

Tests
=====

.. code-block:: bash

    odoo-bin -d <db> -i odoo_forward_auth --test-enable --stop-after-init

For a disposable database and real Nginx integration coverage, run from the
repository root::

    sh tests/integration/run.sh

See ``tests/integration/README.md`` for prerequisites and coverage.
