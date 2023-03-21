# -*- coding: utf-8 -*-
"""
Module for functional test '12_submodule_update' of gitcache.

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
@functional_test("12_submodule_update")
# pylint: disable=too-few-public-methods, invalid-name
class SubmoduleUpdateTest(TestBase):
    """Test the submodule update."""

    def test_submodule_update_single_c(self):
        """Test the 'submodule init' and 'submodule update' with a single '-C' option."""
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        c_option = ["-C", checkout]
        self._perform_submodule_update_test(c_option=c_option)

    def test_submodule_update_multiple_c(self):
        """Test the 'submodule init' and 'submodule update' with multiple '-C' options."""
        c_option = ["-C", self._workspace.workspace_path, "-C", "submodules"]
        self._perform_submodule_update_test(c_option=c_option)

    def test_submodule_update_from_checkout(self):
        """Test the 'submodule init' and 'submodule update' from the checked out repo."""
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        self._perform_submodule_update_test(cwd=checkout)

    def test_submodule_update_module_single_c(self):
        """Test the 'submodule init mod' and 'submodule update mod' with a single '-C' option."""
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        c_option = ["-C", checkout]
        self._perform_submodule_update_module_test(c_option=c_option)

    def test_submodule_update_module_multiple_c(self):
        """Test the 'submodule init mod' and 'submodule update mod' with multiple '-C' options."""
        c_option = ["-C", self._workspace.workspace_path, "-C", "submodules"]
        self._perform_submodule_update_module_test(c_option=c_option)

    def test_submodule_update_module_from_checkout(self):
        """Test the 'submodule init mod' and 'submodule update mod' from the checked out repo."""
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        self._perform_submodule_update_module_test(cwd=checkout)

    def _perform_submodule_update_test(self, c_option=None, cwd=None):
        """Perform the actual test of 'git submodule init' and 'git submodule update'.

        Args:
            c_option (list): The command arguments to change into the directory.
            cwd (str):       The working directory to execute the command from.
        """
        c_option = c_option or []
        repo = "https://github.com/seeraven/submodule-example.git"
        repo_sub1 = "https://github.com/seeraven/dmdcache"
        repo_sub2 = "https://github.com/seeraven/gitcache"
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        # Submodule init does not update the mirror nor does it perform any clones
        self.assert_gitcache_ok(["git"] + c_option + ["submodule", "init"], cwd=cwd)
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)
        self.assert_db_field('clones', repo_sub1, None)
        self.assert_db_field('clones', repo_sub2, None)

        # Submodule update does not update the mirror of this repo ...
        self.assert_gitcache_ok(["git"] + c_option + ["submodule", "update"], cwd=cwd)
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        # ... but it clones the submodule repos
        self.assert_db_field('clones', repo_sub1, 1)
        self.assert_db_field('clones', repo_sub2, 1)

        # Another submodule update updates the mirrors
        self.assert_gitcache_ok(["git"] + c_option + ["submodule", "update"], cwd=cwd)
        self.assert_db_field('mirror-updates', repo_sub1, 1)
        self.assert_db_field('mirror-updates', repo_sub2, 1)
        self.assert_db_field('updates', repo_sub1, 1)
        self.assert_db_field('updates', repo_sub1, 1)

    def _perform_submodule_update_module_test(self, c_option=None, cwd=None):
        """Perform the actual test of 'git submodule init <mod>' and 'git submodule update <mod>'.

        Args:
            c_option (list): The command arguments to change into the directory.
            cwd (str):       The working directory to execute the command from.
        """
        c_option = c_option or []
        repo = "https://github.com/seeraven/submodule-example.git"
        repo_sub1 = "https://github.com/seeraven/dmdcache"
        repo_sub2 = "https://github.com/seeraven/gitcache"
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        # Submodule init does not update the mirror nor does it perform any clones
        path_sub1 = os.path.join(checkout, "dmdcache") if cwd is None else "dmdcache"
        path_sub2 = os.path.join(checkout, "gitcache") if cwd is None else "gitcache"
        self.assert_gitcache_ok(["git"] + c_option + ["submodule", "init", path_sub1], cwd=cwd)
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)
        self.assert_db_field('clones', repo_sub1, None)
        self.assert_db_field('clones', repo_sub2, None)

        # Submodule update with a path updates only that path
        self.assert_gitcache_ok(["git"] + c_option + ["submodule", "update", path_sub1], cwd=cwd)
        self.assert_db_field('clones', repo_sub1, 1)
        self.assert_db_field('clones', repo_sub2, None)

        # Submodule update with --init option also initializes the reference
        self.assert_gitcache_ok(["git"] + c_option + ["submodule", "update",
                                                      "--init", path_sub2], cwd=cwd)
        self.assert_db_field('clones', repo_sub2, 1)

    def test_recursive_init(self):
        """Test 'git submodule update --recursive --init'."""
        repo = "https://github.com/aws/aws-sdk-cpp"
        checkout = os.path.join(self._workspace.workspace_path, "aws-sdk-cpp")
        self.assert_gitcache_ok(["git", "clone", repo, checkout,
                                 "--single-branch", "--branch", "1.9.188"])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        self.assert_gitcache_ok(["git", "submodule", "update", "--recursive", "--init"],
                                cwd=checkout)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-crt-cpp.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-common.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-io.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-compression.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-cal.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-auth.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-http.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-mqtt.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/s2n.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-checksums.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-event-stream.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-c-s3.git', 1)
        self.assert_db_field('clones', 'https://github.com/awslabs/aws-lc.git', 1)

    def test_exclude(self):
        """Test 'git submodule update --init' with one submodule not cached."""
        repo = "https://github.com/seeraven/submodule-example"
        repo_sub1 = "https://github.com/seeraven/dmdcache"
        repo_sub2 = "https://github.com/seeraven/gitcache"
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        self._workspace.set_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX', '.*')
        self._workspace.set_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX',
                                '.*/github\\.com/seeraven/.*dmdcache')
        self.assert_gitcache_ok(["git", "-C", checkout, "submodule", "update", "--init"])
        self.assert_db_field('clones', repo_sub1, None)
        self.assert_db_field('clones', repo_sub2, 1)

    def test_include(self):
        """Test 'git submdoule update --init' with explicitly including one module to be cached."""
        repo = "https://github.com/seeraven/submodule-example"
        repo_sub1 = "https://github.com/seeraven/dmdcache"
        repo_sub2 = "https://github.com/seeraven/gitcache"
        checkout = os.path.join(self._workspace.workspace_path, "submodules")
        self.assert_gitcache_ok(["git", "clone", repo, checkout])
        self.assert_db_field('mirror-updates', repo, 0)
        self.assert_db_field('clones', repo, 1)
        self.assert_db_field('updates', repo, 0)

        self._workspace.set_env('GITCACHE_URLPATTERNS_INCLUDE_REGEX',
                                '.*/github\\.com/seeraven/.*dmdcache')
        self._workspace.set_env('GITCACHE_URLPATTERNS_EXCLUDE_REGEX', '')
        self.assert_gitcache_ok(["git", "-C", checkout, "submodule", "update", "--init"])
        self.assert_db_field('clones', repo_sub1, 1)
        self.assert_db_field('clones', repo_sub2, None)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
