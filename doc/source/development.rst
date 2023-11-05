Development Documentation
=========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   dev_styleguide
   dev_unittests
   dev_workflow
   API Documentation <apidoc/git_cache>


Introduction
------------

This section defines the general development guidelines of the |project_name|
package.

To ensure a high quality software product, the following topics are covered
through various tools:

- A common style guide as described in :doc:`dev_styleguide`:

  - Ensuring a common style, here the PEP8 style, by using the tools pylint_,
    pycodestyle_ and flake8_. The style can be checked by calling::

        $ make check-style.venv

- A well tested software:

  - Performing a static code analysis using the tools flake8_ and pylint_. To
    perform the static code analysis, call::

        $ make check-style.venv
      
  - Ensure the functionality of the individual components by performing
    :doc:`dev_unittests`. To execute the tests, call::

        $ make unittests.venv
      
  - Ensure the functionality of the application by performing various custom
    `blackbox` tests. To execute the tests, call::
    
        $ make functional-tests.venv

  - Ensure a high code coverage by the unit- and functional tests. To measure
    the code coverage, call::

        $ make tests-coverage.venv

- A documentation:

  - Generate the user and developer documentation using sphinx_::

        $ make doc.venv

  - Generate the man page also using sphinx_::

        $ make man.venv

  - Changes are documented in the `git` repository. By enforcing a common style
    on the commit messages through git hooks, these comments can directly be
    used to generate a `Changelog`.

- A development workflow as described in :doc:`dev_workflow`.


Makefile Support
----------------

All available checks and tests are available using the provided
``Makefile``. To see a list of all available targets, call::

    $ make help

For a developer, the default target performs all tests in a virtual python
environment::

    $ make


.. _pycodestyle: https://pypi.org/project/pycodestyle/
.. _pylint: https://www.pylint.org/
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/master/
