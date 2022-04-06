# -*- coding: utf-8 -*-
"""
Module for functional test '21_cleanup' of gitcache.

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
import time

from .helpers.test_base import TestBase
from .helpers.test_registry import functional_test


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Functional Test
# -----------------------------------------------------------------------------
@functional_test("21_cleanup")
# pylint: disable=too-few-public-methods
class CleanupTest(TestBase):
    """Test the cleanup support."""

    def test_cleanup(self):
        """Test the 'git cleanup' command."""
        # Initial clone
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        mirror_dir = os.path.join(self._workspace.gitcache_dir_path, "mirrors",
                                  "github.com", "seeraven", "gitcache")
        mirror_file = os.path.join(mirror_dir, "git", "config")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_file_exists(mirror_file)
        self.assert_file_exists(mirror_dir)

        # Cleanup with 'git cleanup' outside the cleanup time
        self.assert_gitcache_ok(["git", "cleanup"])
        self.assert_gitcache_ok(["-c"])
        self.assert_db_field('mirror-updates', repo, 0)

        # Cleanup
        self._workspace.set_env('GITCACHE_CLEANUP_AFTER', '1')
        time.sleep(2.0)
        self.assert_gitcache_ok(["git", "cleanup"])
        self.assert_db_field('mirror-updates', repo, None)
        self.assert_file_does_not_exist(mirror_file)
        self.assert_file_does_not_exist(mirror_dir)

        # Clone again
        checkout = os.path.join(self._workspace.workspace_path, "gitcache2")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_file_exists(mirror_file)
        self.assert_file_exists(mirror_dir)

        # Cleanup with 'gitcache -c'
        time.sleep(2.0)
        self.assert_gitcache_ok(["-c"])
        self.assert_db_field('mirror-updates', repo, None)
        self._workspace.del_env('GITCACHE_CLEANUP_AFTER')
        self.assert_file_does_not_exist(mirror_file)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
