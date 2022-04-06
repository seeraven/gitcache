# -*- coding: utf-8 -*-
"""
Module for functional test '13_fetch' of gitcache.

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
@functional_test("13_fetch")
# pylint: disable=too-few-public-methods
class FetchTest(TestBase):
    """Test the fetch."""

    def test_fetch(self):
        """Test the 'git fetch' command."""
        # Initial clone
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])

        # Fetch updates the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "fetch"])
        self.assert_db_field('mirror-updates', repo, 1)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 1)

        # Fetch with explicit origin url updates the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "fetch", repo])
        self.assert_db_field('mirror-updates', repo, 2)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 2)

        # Fetch with origin ref updates the mirror
        self.assert_gitcache_ok(["git", "-C", checkout, "fetch", "origin"])
        self.assert_db_field('mirror-updates', repo, 3)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 3)

        # Fetch outside update interval does not update the mirror
        self._workspace.set_env('GITCACHE_UPDATE_INTERVAL', '3600')
        self.assert_gitcache_ok(["git", "-C", checkout, "fetch"])
        self.assert_db_field('mirror-updates', repo, 3)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 4)
        self._workspace.del_env('GITCACHE_UPDATE_INTERVAL')

        # Fetch from within directory
        self.assert_gitcache_ok(["git", "fetch", repo], cwd=checkout)
        self.assert_db_field('mirror-updates', repo, 4)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 5)

    def test_fetch_from_local_fs(self):
        """Test not caching fetches from local filesystem."""
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "-C", self._workspace.workspace_path, "clone", repo])

        checkout2 = os.path.join(self._workspace.workspace_path, "gitcache2")
        self.assert_gitcache_ok(["git", "clone", checkout, checkout2])
        self.assert_gitcache_ok(["git", "remote", "set-url", "origin", repo], cwd=checkout)

        self.assert_gitcache_ok(["git", "-C", checkout2, "fetch"])
        self.assert_db_field('clones', checkout, None)

    def test_exclude(self):
        """Test fetching an excluded url."""
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        self._workspace.set_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX', '.*')
        self._workspace.set_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX', '.*/github\\.com/.*')
        self.assert_gitcache_ok(["git", "-C", checkout, "fetch", repo])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)
        self._workspace.del_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX')
        self._workspace.del_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX')

    def test_include(self):
        """Test fetching an included url."""
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        self._workspace.set_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX', '.*/github\\.com/.*')
        self._workspace.set_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX', '')
        self.assert_gitcache_ok(["git", "-C", checkout, "fetch", repo])
        self.assert_db_field('mirror-updates', repo, 1)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 1)
        self._workspace.del_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX')
        self._workspace.del_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX')


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
