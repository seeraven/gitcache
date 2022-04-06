# -*- coding: utf-8 -*-
"""
Module for functional test '16_checkout' of gitcache.

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
@functional_test("16_checkout")
# pylint: disable=too-few-public-methods
class CheckoutTest(TestBase):
    """Test the checkout support."""

    def test_checkout(self):
        """Test the 'git checkout' command."""
        # Initial clone
        repo = "https://github.com/seeraven/lfs-example.git"
        checkout = os.path.join(self._workspace.workspace_path, "lfs-example")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('lfs-updates', repo, 1)

        # Modify a file and perform checkout call to restore it
        os.unlink(os.path.join(checkout, "README.md"))
        self.assert_gitcache_ok(["git", "-C", checkout, "checkout", "README.md"])
        self.assert_in_file("git-lfs", os.path.join(checkout, "README.md"))

        # Checkout to switch to a branch
        self.assert_gitcache_ok(["git", "-C", checkout, "checkout", "main"])

        # Checkout to switch to a branch should fetch additional files
        self.assert_gitcache_ok(["git", "-C", checkout, "checkout", "extra_branch"])

        lfs_obj_file = os.path.join(
            *[self._workspace.gitcache_dir_path,
              "mirrors", "github.com", "seeraven", "lfs-example", "lfs", "objects", "c0", "c9",
              "c0c955aa4aa976424645d86e82ba4452bb715364171e7db3bf715214b2cfb99d"])
        self.assert_file_exists(lfs_obj_file)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
