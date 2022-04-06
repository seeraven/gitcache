# -*- coding: utf-8 -*-
"""
Module for functional test '20_update_all' of gitcache.

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
@functional_test("20_update_all")
# pylint: disable=too-few-public-methods
class UpdateAllTest(TestBase):
    """Test the update-mirrors support."""

    def test_update_all(self):
        """Test the 'git update-mirrors' command."""
        # Update command without any mirrors
        self.assert_gitcache_ok(["git", "update-mirrors"])
        self.assert_gitcache_ok(["-u"])

        # Initial clone
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)

        # Update with 'git update-mirrors'
        self.assert_gitcache_ok(["git", "update-mirrors"])
        self.assert_db_field('mirror-updates', repo, 1)

        # Update with 'gitcache -u'
        self.assert_gitcache_ok(["-u"])
        self.assert_db_field('mirror-updates', repo, 2)

        # Explicit update ignores update interval
        self._workspace.set_env('GITCACHE_UPDATE_INTERVAL', '3600')
        self.assert_gitcache_ok(["git", "update-mirrors"])
        self.assert_db_field('mirror-updates', repo, 3)
        self._workspace.del_env('GITCACHE_UPDATE_INTERVAL')

        # Failed update reflected in return code
        mirror_dir = os.path.join(self._workspace.gitcache_dir_path, "mirrors",
                                  "github.com", "seeraven", "gitcache", "git")
        self.assert_gitcache_ok(["git", "remote", "set-url", "origin",
                                 "https://github.com/seeraven/gatcache.git"], cwd=mirror_dir)
        self.assert_gitcache_fails(["git", "update-mirrors"])
        self.assert_db_field('mirror-updates', repo, 3)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
