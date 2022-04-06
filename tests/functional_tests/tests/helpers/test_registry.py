# -*- coding: utf-8 -*-
"""
Module for the class registry of the functional tests of gitcache.

Copyright:
    2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import importlib
import logging
import pkgutil
import sys


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Registry
# -----------------------------------------------------------------------------
_TEST_CLASSES = {}


def functional_test(name):
    """Decorate a test class to add it to the registry.

    Args:
        name (str): The name of the functional test.
    """
    def decorator(cls):
        LOG.debug("Register functional test %s", name)
        _TEST_CLASSES[name] = cls
        return cls
    return decorator


def initialize_registry(parent_name, directory):
    """Initialize the registry by importing all modules within the given directory.

    Args:
        parent_name (str): Name of the parent module.
        directory (str):   The directory containing the modules to import.
    """
    LOG.debug("Initialize registry by importing all modules of the directory %s",
              directory)
    for _, module_name, _ in pkgutil.iter_modules([directory]):
        if module_name not in sys.modules and module_name != 'main':
            LOG.debug("Importing module %s", module_name)
            _ = importlib.import_module(f"{parent_name}.{module_name}")


def get_available_tests():
    """Return a (sorted) list of available tests."""
    return sorted(_TEST_CLASSES.keys())


def get_test_objs(settings):
    """Return a map with test names as keys and instantiated tests as values.

    Args:
        settings (obj): The settings object.

    Return:
        Returns a map with the test name as key and the instrantiated test as
        the value.
    """
    obj_map = {}
    for test_name in settings.selected_tests:
        if test_name not in _TEST_CLASSES:
            continue
        obj_map[test_name] = _TEST_CLASSES[test_name]()
    return obj_map


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
