Unit Tests
==========

Unit tests ensure that the individual parts of your software work as expected.
The benefit of unit tests are often visible when you are modifiing the software
long after you have initially written it, e.g., if you are changing or extending
it. In contrast to `integration tests` or `blackbox tests`, unit tests use the
information about the internal structure of the components and are also called
`whitebox tests`.


Writing Unit Tests
------------------

The unit tests are executed using the nose_ framework and are located in the
:code:`tests` directory.

To add more tests, all you have to do is to add a new python file containing
your test case.


Executing Unit Tests
--------------------

To execute the unit tests, call::

    $ make unittests.venv


Unit Test Code Coverage
-----------------------

The amount of lines covered by unit tests is often used as a metric to interpret
the code quality. This might be misleading, since some developers concentrate
more on `blackbox tests`. In addition, parts that deal with exceptions like
hardware failure are difficult to test, so that enforcing a coverage of 100% is
usually not a good idea.

To show the unittests code coverage, call::

    $ make unittests-coverage.venv

This shows you the coverage on the standard output an throws an error if the
coverage is too low. It also generates an HTML report ``doc/coverage/index.html``
that you can view using your favorite browser.


.. _nose: https://nose.readthedocs.io/en/latest/
