# -*- coding: utf-8 -*-
"""
Module for functional test '11_pull' of gitcache.

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
@functional_test("11_pull")
# pylint: disable=too-few-public-methods
class PullTest(TestBase):
    """Test the pull."""

    def test_pull(self):
        """Test the 'git pull' command."""
        # Initial clone
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])

        # Pull updates the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "pull"])
        self.assert_db_field('mirror-updates', repo, 1)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 1)

        # Pull with multiple -C options updates the mirror as well
        self.assert_gitcache_ok(["git", "-C", self._workspace.workspace_path,
                                 "-C", "gitcache", "pull"])
        self.assert_db_field('mirror-updates', repo, 2)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 2)

        # Pull inside the checked out repository updates the mirror as well
        self.assert_gitcache_ok(["git", "pull"], cwd=checkout)
        self.assert_db_field('mirror-updates', repo, 3)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 3)

        # Pull without updating the mirror due to update interval
        self._workspace.set_env('GITCACHE_UPDATE_INTERVAL', '3600')
        self.assert_gitcache_ok(["git", "-C", checkout, "pull"])
        self.assert_db_field('mirror-updates', repo, 3)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 4)
        self._workspace.del_env('GITCACHE_UPDATE_INTERVAL')

        # Pull with repository specification
        self.assert_gitcache_ok(["git", "-C", checkout, "pull", "origin"])
        self.assert_db_field('mirror-updates', repo, 4)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 5)

        # Pull with repository and ref specification
        self.assert_gitcache_ok(["git", "-C", checkout, "pull", "origin", "master"])
        self.assert_db_field('mirror-updates', repo, 5)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 6)

        # Do not update mirror if repository does not use the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "remote", "set-url", "origin", repo])
        self.assert_gitcache_ok(["git", "-C", checkout, "pull"])
        self.assert_db_field('mirror-updates', repo, 5)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 6)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
