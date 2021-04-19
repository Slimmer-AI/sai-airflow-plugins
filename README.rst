sai-airflow-plugins
===================

|pypi version| |build status| |docs status|

.. |pypi version| image:: https://pypip.in/version/sai-airflow-plugins/badge.svg
                  :target: https://pypi.org/project/sai-airflow-plugins/
.. |build status| image:: https://github.com/Slimmer-AI/sai-airflow-plugins/actions/workflows/python-package.yml/badge.svg
.. |docs status| image:: https://github.com/Slimmer-AI/sai-airflow-plugins/actions/workflows/github-pages.yml/badge.svg

``sai-airflow-plugins`` is a Python package that contains various operators, hooks and utilities for Apache Airflow.

Full documentation is available at https://slimmer-ai.github.io/sai-airflow-plugins/.


Features
--------

- Hook, operator and sensor for executing an SSH command using the `Fabric <https://www.fabfile.org/>`_ library,
  with support for adding output responders
- Operator for sending messages to an
  `incoming Mattermost webhook <https://docs.mattermost.com/developer/webhooks-incoming.html>`_
- Conditional operators and sensors that are skipped when a Python callable evaluates to ``False``


Installation
------------

Through pip (PyPI):

.. code-block:: bash

    pip install sai-airflow-plugins

From source:

.. code-block:: bash

    python setup.py install


Documentation
-------------

If you want to build the documentation, please install the documentation dependencies by executing:

.. code-block:: bash

    pip install sai-airflow-plugins[docs]

or

.. code-block:: bash

    pip install .[docs]

Documentation can be built by executing:

.. code-block:: bash

    python setup.py build_docs

Documentation can also be build from the ``docs`` folder directly. In that case ``sai-airflow-plugins`` should be
installed and available in your current working environment. Execute:

.. code-block:: bash

    make html

in the ``docs`` folder.
