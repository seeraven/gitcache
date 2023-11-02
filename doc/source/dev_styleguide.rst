Style Guide
===========

Style Guide for Python Code
---------------------------

The python source files must be formatted according to the python PEP8_ style
that is also checked by the pycodestyle_, pylint_ and flake8_ tools. To perform
all the checks, call::

    $ make check-style.venv

The only exception to the PEP8_ style is a not so strict interpretation of
whitespaces. This is configured in the configuration files :code:`.pylintrc`,
:code:`.pycodestyle` and :code:`setup.cfg`. The reason is to allow a more
readable formatting.


Style Guide for Inline Documentation
------------------------------------

For the documentation, all elements must be documented for sphinx_ using the
`Google Python Style Guide`_. See also the `Google Python Style Guide Example`_.


.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _pycodestyle: https://pypi.org/project/pycodestyle/
.. _pylint: https://www.pylint.org/
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/master/
.. _`Google Python Style Guide`: https://github.com/google/styleguide/blob/gh-pages/pyguide.md
.. _`Google Python Style Guide Example`: http://www.sphinx-doc.org/en/master/usage/extensions/example_google.html
