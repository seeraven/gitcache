# -*- coding: utf-8 -*-
"""
Module for functional test '04_bail_out_options' of gitcache.

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
@functional_test("04_bail_out_options")
class BailOutOptionsTest(TestBase):
    """Test all bail out options."""

    def test_git_version(self):
        """Test bail out option '--version' of git."""
        self.assert_gitcache_ok(["git", "--version"])

    def test_git_exec_path(self):
        """Test bail out option '--exec-path' of git."""
        self.assert_gitcache_ok(["git", "--exec-path"])

    def test_git_html_path(self):
        """Test bail out option '--html-path' of git."""
        self.assert_gitcache_ok(["git", "--html-path"])

    def test_git_man_path(self):
        """Test bail out option '--man-path' of git."""
        self.assert_gitcache_ok(["git", "--man-path"])

    def test_git_info_path(self):
        """Test bail out option '--info-path' of git."""
        self.assert_gitcache_ok(["git", "--info-path"])


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
