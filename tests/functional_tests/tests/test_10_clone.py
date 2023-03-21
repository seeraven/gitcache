# -*- coding: utf-8 -*-
"""
Module for functional test '10_clone' of gitcache.

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
@functional_test("10_clone")
# pylint: disable=too-few-public-methods
class CloneTest(TestBase):
    """Test the cloning."""

    def test_clone_without_argument(self):
        """Test the 'git clone' command without an argument to clone."""
        self.assert_gitcache_fails(["git", "clone"])

    def test_clone_error(self):
        """Test the 'git clone' command with an wrong url to clone."""
        # Note: Cloning from a nonexistant source of github.com asks
        #       for a login on Windows. Therefore, we use a nonexistant
        #       URL.
        repo = "https://does.not.exist.com/nonexistant"
        checkout = os.path.join(self._workspace.workspace_path, "dummy")
        self.assert_gitcache_fails(["git", "clone", repo, checkout])

    def test_clone(self):
        """Test the 'git clone' command."""
        # Initial clone
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "-C", self._workspace.workspace_path, "clone", repo])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_remote_of_clone(checkout)
        self.assert_branch(checkout, "master")

        # Second clone with update of the mirror
        checkout = os.path.join(self._workspace.workspace_path, "gitcache2")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 1)
        self.assert_db_field('clones', repo, 2)
        self.assert_remote_of_clone(checkout)

        # Third clone without updating the mirror
        self._workspace.set_env('GITCACHE_UPDATE_INTERVAL', '3600')
        checkout = os.path.join(self._workspace.workspace_path, "gitcache3")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 1)
        self.assert_db_field('clones', repo, 3)
        self.assert_remote_of_clone(checkout)
        self._workspace.del_env('GITCACHE_UPDATE_INTERVAL')

        # Fourth clone with updating the mirror
        checkout = os.path.join(self._workspace.workspace_path, "gitcache4")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 2)
        self.assert_db_field('clones', repo, 4)
        self.assert_remote_of_clone(checkout)

    def test_clone_from_local_fs(self):
        """Test not caching clones from local filesystem."""
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_ok(["git", "-C", self._workspace.workspace_path, "clone", repo])

        repo = checkout
        checkout = os.path.join(self._workspace.workspace_path, "gitcache2")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('clones', repo, None)

    def test_clone_branch(self):
        """Test cloning an explicit branch."""
        repo = "https://github.com/seeraven/scm-autologin-plugin"
        branch = "feature_ownUserType"
        checkout = os.path.join(self._workspace.workspace_path, "scm-autologin-plugin")
        self.assert_gitcache_ok(["git", "clone", "--branch", branch, repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_remote_of_clone(checkout)
        self.assert_branch(checkout, branch)

        checkout = os.path.join(self._workspace.workspace_path, "scm-autologin-plugin2")
        self.assert_gitcache_ok(["git", "clone", repo, checkout, "-b", branch])
        self.assert_db_field('mirror-updates', repo, 1)
        self.assert_db_field('clones', repo, 2)
        self.assert_remote_of_clone(checkout)
        self.assert_branch(checkout, branch)

    def test_clone_tag(self):
        """Test cloning an explicit tag."""
        repo = "https://github.com/seeraven/scm-autologin-plugin"
        tag = "1.0-scm1.60"
        checkout = os.path.join(self._workspace.workspace_path, "scm-autologin-plugin")
        self.assert_gitcache_ok(["git", "clone", "--branch", tag, repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_remote_of_clone(checkout)
        self.assert_tag(checkout, tag)

    def test_exclude(self):
        """Test cloning an excluded url."""
        repo = "https://github.com/seeraven/scm-autologin-plugin"
        checkout = os.path.join(self._workspace.workspace_path, "scm-autologin-plugin")
        self._workspace.set_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX', '.*')
        self._workspace.set_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX',
                                '.*/github\\.com/seeraven/scm-.*')
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, None)
        self._workspace.del_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX')
        self._workspace.del_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX')

    def test_include(self):
        """Test cloning an included url."""
        repo = "https://github.com/seeraven/scm-autologin-plugin"
        checkout = os.path.join(self._workspace.workspace_path, "scm-autologin-plugin")
        self._workspace.set_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX',
                                '.*/github\\.com/seeraven/scm-.*')
        self._workspace.set_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX', '')
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self._workspace.del_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX')
        self._workspace.del_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX')

    def test_aborted_clone(self):
        """Test aborting the first clone command and cloning again."""
        repo = "https://github.com/seeraven/gitcache.git"
        checkout = os.path.join(self._workspace.workspace_path, "gitcache")
        self.assert_gitcache_abort(["git", "-C", self._workspace.workspace_path, "clone", repo])
        self.assert_db_field('mirror-updates', repo, None)
        self.assert_db_field('clones', repo, None)

        self.assert_gitcache_ok(["git", "-C", self._workspace.workspace_path, "clone", repo])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_remote_of_clone(checkout)
        self.assert_branch(checkout, "master")


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
