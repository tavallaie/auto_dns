===================
Auto DNS Python CLI
===================

Auto DNS is a Python command line application which automatically updates the DNS records of your domain using various DNS providers.

Supported DNS providers:

- Arvan
- Cloudflare

This library is intended to be used on a system with a dynamic public IP that you want to map to a static domain name.

Installation
============

The package can be installed using pip:

.. code-block:: shell

   $ pip install auto-dns

Or if you prefer, you can use Poetry:

.. code-block:: shell

   $ poetry add auto-dns

Configuration
=============

To configure a DNS provider API key, use the following command:

.. code-block:: shell

   $ autodns set_api_key <provider> <api_key>

Usage
=====

To update a DNS record with your current public IP, use the following command:

.. code-block:: shell

   $ autodns update <domain> <record_type> <provider>

Contributing
============

Contributions are welcome! Please feel free to submit a Pull Request.

License
=======

Auto DNS is released under the MIT License.
