# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.git_command module."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import os
from unittest import TestCase
from unittest import mock

import git_cache.git_command


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def mockenv(**envvars):
    """Set up a temporary new environment."""
    return mock.patch.dict(os.environ, envvars)


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheGitCommandTest(TestCase):
    """Test the :mod:`git_cache.git_command` module."""

    @mockenv(GITCACHE_DISABLE="")
    def test_is_gitcache_disabled_false(self):
        """git_cache.git_command: Disable flag is false by default."""
        self.assertFalse(git_cache.git_command.is_gitcache_disabled())

    @mockenv(GITCACHE_DISABLE="true")
    def test_is_gitcache_disabled_true(self):
        """git_cache.git_command: Disable flag is true for accepted values."""
        self.assertTrue(git_cache.git_command.is_gitcache_disabled())

    @mockenv(GITCACHE_DISABLE="ON")
    def test_is_gitcache_disabled_true_case_insensitive(self):
        """git_cache.git_command: Disable flag matching is case insensitive."""
        self.assertTrue(git_cache.git_command.is_gitcache_disabled())

    @mockenv(GITCACHE_DISABLE="0")
    def test_is_gitcache_disabled_unhandled_value(self):
        """git_cache.git_command: Disable flag ignores unsupported values."""
        self.assertFalse(git_cache.git_command.is_gitcache_disabled())

    @mockenv(GITCACHE_DISABLE="1")
    @mock.patch("git_cache.git_command.call_real_git", return_value=23)
    def test_handle_git_command_disabled_calls_real_git(self, call_real_git_mock):
        """git_cache.git_command: Disabled mode always forwards to real git."""
        with self.assertRaises(SystemExit) as cm:
            git_cache.git_command.handle_git_command(["git"], ["clone", "repo"])

        self.assertEqual(23, cm.exception.code)
        call_real_git_mock.assert_called_once_with(["clone", "repo"])


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
