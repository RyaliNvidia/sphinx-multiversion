.. _faq:

==========================
Frequently Asked Questions
==========================

Why another tool for versioning Sphinx docs?
============================================

While there are several sphinx extensions out there (e.g.  `sphinxcontrib-versioning <sphinxcontrib_versioning_>`_  or `sphinx-versions <sphinx_versions_>`_) none of them seem to work correctly with recent sphinx versions (as of March 2020).
Their code heavily relies on monkey-patching Sphinx internals at runtime, which is error-prone and makes the code a mess.

In contrast, the extension part of ``sphinx-multiversion`` does not do any fancy patching, it just provides some HTML context variables.


How does it work?
=================

Instead of running `sphinx build`, just run `sphinx-multiversion` from the root of your Git repository.
It reads your Sphinx :file:`conf.py` file from the currently checked out Git branch for configuration, then generates a list of versions from local or remote tags and branches.
This data is written to a JSON file - if you want to have a look what data will be generated, you can use the ``--dump-metadata`` flag.

Then it copies the data for each version into separate temporary directories, builds the documentation from each of them and writes the output to the output directory.
Each version is built with the :file:`conf.py` file from that version's
temporary checkout.
The currently checked out branch still controls which refs are selected and
which initial ``sphinx-multiversion`` settings are used.


Do I need to make changes to old branches or tags?
==================================================

Yes. Each branch or tag must contain a :file:`conf.py` file that can build
that version's documentation with your installed dependencies.

This lets branches evolve their documentation configuration independently.
The tradeoff is that old branches may need small compatibility fixes if their
:file:`conf.py` files no longer work with your current documentation
dependencies.


What are the license terms of ``sphinx-multiversion``?
======================================================

``sphinx-multiversion`` is licensed under the terms of the `BSD 2-Clause license <bsd_2clause_license_>`_.


.. _sphinxcontrib_versioning: https://github.com/sphinx-contrib/sphinxcontrib-versioning
.. _sphinx_versions: https://github.com/Smile-SA/sphinx-versions
.. _bsd_2clause_license: https://choosealicense.com/licenses/bsd-2-clause/
