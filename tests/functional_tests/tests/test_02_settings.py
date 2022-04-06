# -*- coding: utf-8 -*-
"""
Module for functional test '02_settings' of gitcache.

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
import logging

from .helpers.test_base import TestBase
from .helpers.test_registry import functional_test


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Functional Test
# -----------------------------------------------------------------------------
@functional_test("02_settings")
# pylint: disable=too-few-public-methods
class SettingsTest(TestBase):
    """Test the settings output."""

    def test_settings(self):
        """Test the output of the 'gitcache' command that prints the settings."""
        self.assert_gitcache_output([], "settings")
        self.assert_gitcache_config_exists()
        self.assert_gitcache_db_does_not_exist()

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
