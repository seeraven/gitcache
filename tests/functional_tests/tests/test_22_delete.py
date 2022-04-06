# -*- coding: utf-8 -*-
"""
Module for functional test '22_delete' of gitcache.

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
@functional_test("22_delete")
# pylint: disable=too-few-public-methods
class DeleteTest(TestBase):
    """Test the delete mirror support."""

    def test_delete(self):
        """Test the 'git delete-mirror' command."""
        # Initial clone
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)

        # Delete giving the URL
        self.assert_gitcache_ok(["git", "delete-mirror", repo])
        self.assert_db_field('mirror-updates', repo, None)

        # Delete giving the path
        checkout = os.path.join(self._workspace.workspace_path, "gitcache2")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)

        mirror_dir = os.path.join(self._workspace.gitcache_dir_path, "mirrors",
                                  "github.com", "seeraven", "gitcache")
        self.assert_gitcache_ok(["git", "delete-mirror", mirror_dir])
        self.assert_db_field('mirror-updates', repo, None)

        # Delete using 'gitcache -d' command
        checkout = os.path.join(self._workspace.workspace_path, "gitcache3")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)

        self.assert_gitcache_ok(["-d", repo])
        self.assert_db_field('mirror-updates', repo, None)

        # Delete using 'gitcache -d' command giving the path
        checkout = os.path.join(self._workspace.workspace_path, "gitcache4")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)

        self.assert_gitcache_ok(["-d", mirror_dir])
        self.assert_db_field('mirror-updates', repo, None)

        # Delete using invalid URL
        self.assert_gitcache_fails(["-d", "https://github.com/seeraven/gatcache.git"])

        # Delete using invalid path
        mirror_dir = os.path.join(self._workspace.gitcache_dir_path, "mirrors",
                                  "github.com", "seeraven", "gatcache")
        self.assert_gitcache_fails(["-d", mirror_dir])

        # Delete more than one mirror at once
        checkout = os.path.join(self._workspace.workspace_path, "gitcache5")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)

        repo2 = "https://github.com/seeraven/submodule-example"
        checkout2 = os.path.join(self._workspace.workspace_path, "submodule-example")
        self.assert_gitcache_ok(["git", "clone", repo2, checkout2])
        self.assert_db_field('mirror-updates', repo2, 0)

        self.assert_gitcache_ok(["-d", repo, "-d", repo2])
        self.assert_db_field('mirror-updates', repo, None)
        self.assert_db_field('mirror-updates', repo2, None)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
