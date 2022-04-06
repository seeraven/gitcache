# -*- coding: utf-8 -*-
"""
Module for functional test '03_statistics' of gitcache.

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
import os

from .helpers.test_base import TestBase
from .helpers.test_registry import functional_test


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Functional Test
# -----------------------------------------------------------------------------
@functional_test("03_statistics")
# pylint: disable=too-few-public-methods
class StatisticsTest(TestBase):
    """Test the statistics output."""

    def test_statistics(self):
        """Test the statistics output of the 'gitcache -s' command."""
        repo = "https://github.com/seeraven/gitcache.git"

        self.assert_gitcache_output(["-s"], "init_stats")
        self.assert_gitcache_config_does_not_exist()
        self.assert_gitcache_db_does_not_exist()

        self.assert_gitcache_ok(["git", "clone", repo,
                                 os.path.join(self._workspace.workspace_path, 'gitcache')])
        self.assert_gitcache_config_exists()
        self.assert_gitcache_db_exists()
        self.assert_db_field('clones', repo, 1)

        self.assert_gitcache_output(["-s"], "clone_stats")

        self.assert_gitcache_ok(["-z"])
        self.assert_db_field('clones', repo, 0)
        self.assert_gitcache_output(["-s"], "clone_zeroed_stats")


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
