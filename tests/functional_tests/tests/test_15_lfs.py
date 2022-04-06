# -*- coding: utf-8 -*-
"""
Module for functional test '15_lfs' of gitcache.

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
@functional_test("15_lfs")
# pylint: disable=too-few-public-methods
class LfsTest(TestBase):
    """Test the lfs support."""

    def test_lfs_fetch(self):
        """Test the 'git lfs fetch' command."""
        # Initial clone
        repo = "https://github.com/seeraven/lfs-example.git"
        checkout = os.path.join(self._workspace.workspace_path, "lfs-example")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('lfs-updates', repo, 1)

        # Included files by lfs configuration should be checked out
        self.assert_not_in_file("oid sha256", os.path.join(checkout, "included", "first.png"))
        self.assert_in_file("oid sha256", os.path.join(checkout, "excluded", "first.png"))

        # git lfs fetch commands that do not update the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "fetch"])
        self.assert_db_field('lfs-updates', repo, 1)

        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "fetch", "origin"])
        self.assert_db_field('lfs-updates', repo, 1)

        # git lfs fetch commands that update the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "fetch",
                                 "--include", "*", "--exclude", ""])
        self.assert_db_field('lfs-updates', repo, 2)

        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "fetch", "origin",
                                 "--include", "*", "--exclude", ""])
        self.assert_db_field('lfs-updates', repo, 3)

        # git lfs fetch commands update the mirror even if outside the update interval
        self._workspace.set_env('GITCACHE_UPDATE_INTERVAL', '3600')
        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "fetch",
                                 "--include", "*", "--exclude", ""])
        self.assert_db_field('lfs-updates', repo, 4)
        self._workspace.del_env('GITCACHE_UPDATE_INTERVAL')

        # The excluded file must not be updated by the fetch (only by a pull)
        self.assert_in_file("oid sha256", os.path.join(checkout, "excluded", "first.png"))

        # git lfs pull with update of the mirror and checkout of excluded files
        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "pull",
                                 "--include", "*", "--exclude", ""])
        self.assert_db_field('lfs-updates', repo, 5)
        self.assert_not_in_file("oid sha256", os.path.join(checkout, "excluded", "first.png"))

    def test_lfs_pull(self):
        """Test not caching ls-remotes from local filesystem."""
        repo = "https://github.com/seeraven/lfs-example.git"
        checkout = os.path.join(self._workspace.workspace_path, "lfs-example")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('lfs-updates', repo, 1)

        # Included files by lfs configuration should be checked out
        self.assert_not_in_file("oid sha256", os.path.join(checkout, "included", "first.png"))
        self.assert_in_file("oid sha256", os.path.join(checkout, "excluded", "first.png"))

        # git lfs pull commands that do not update the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "pull"])
        self.assert_db_field('lfs-updates', repo, 1)

        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "pull", "origin"])
        self.assert_db_field('lfs-updates', repo, 1)

        # git lfs pull commands that update the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "lfs", "pull",
                                 "--include", "*", "--exclude", ""])
        self.assert_db_field('lfs-updates', repo, 2)

        # Excluded entry is now checked out
        self.assert_not_in_file("oid sha256", os.path.join(checkout, "excluded", "first.png"))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
