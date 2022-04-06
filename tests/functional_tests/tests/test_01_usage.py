# -*- coding: utf-8 -*-
"""
Module for functional test '01_usage' of gitcache.

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
@functional_test("01_usage")
# pylint: disable=too-few-public-methods
class UsageTest(TestBase):
    """Test of the help text."""

    def test_usage(self):
        """Test of the help text of the gitcache command."""
        self.assert_gitcache_output(["-h"], "usage")
        self.assert_gitcache_config_does_not_exist()


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
