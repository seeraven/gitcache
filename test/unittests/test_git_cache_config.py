# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.config module."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import importlib
import os
from unittest import TestCase

import mock

import git_cache.config
import git_cache.global_settings


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def mockenv(**envvars):
    """Set up a temporary new environment."""
    return mock.patch.dict(os.environ, envvars)


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheConfigTest(TestCase):
    """Test the :class:`git_cache.config.Config` class."""

    def setUp(self):
        """Set up the test case."""
        if os.path.exists("/tmp/config"):
            os.unlink("/tmp/config")

    def tearDown(self):
        """Tear down the test case."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.config)

        if os.path.exists("/tmp/config"):
            os.unlink("/tmp/config")

    @mockenv(GITCACHE_DIR="/tmp")
    def test_defaults(self):
        """git_cache.config.Config: Default entries."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.config)
        config = git_cache.config.Config()

        expected_git_cmd = git_cache.config._find_git()  # pylint: disable=protected-access

        self.assertEqual(config.get("System", "RealGit"), expected_git_cmd)
        self.assertEqual(config.get("MirrorHandling", "UpdateInterval"), 0)
        self.assertEqual(config.get("MirrorHandling", "CleanupAfter"), 14 * 24 * 60 * 60)
        self.assertEqual(config.get("LFS", "Retries"), 3)
        self.assertEqual(config.get("LFS", "CommandTimeout"), 60 * 60)
        self.assertEqual(config.get("LFS", "OutputTimeout"), 5 * 60)
        self.assertEqual(config.get("LFS", "PerMirrorStorage"), True)

    @mockenv(GITCACHE_DIR="/tmp", GITCACHE_CLONE_COMMAND_TIMEOUT="a")
    def test_timeparse_error(self):
        """git_cache.config.Config: Test time parser error."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.config)
        config = git_cache.config.Config()
        self.assertEqual(config.get("Clone", "CommandTimeout"), 0)

    @mockenv(GITCACHE_DIR="/tmp", GITCACHE_UPDATE_INTERVAL="-1", GITCACHE_LFS_PER_MIRROR_STORAGE="0")
    def test_env_default(self):
        """git_cache.config.Config: Test overwrite using environment variable."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.config)
        config = git_cache.config.Config()
        self.assertEqual(config.get("MirrorHandling", "UpdateInterval"), -1)
        self.assertEqual(config.get("LFS", "PerMirrorStorage"), False)

    @mockenv(GITCACHE_DIR="/tmp")
    def test_load(self):
        """git_cache.config.Config: Load from file."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.config)
        with open("/tmp/config", "w", encoding="utf-8") as file_handle:
            file_handle.write(
                """
[MirrorHandling]
UpdateInterval = -1

[LFS]
permirrorstorage = false
"""
            )
        config = git_cache.config.Config()
        self.assertEqual(config.get("MirrorHandling", "UpdateInterval"), -1)
        self.assertEqual(config.get("LFS", "PerMirrorStorage"), False)

    @mockenv(GITCACHE_DIR="/tmp")
    def test_str_rep(self):
        """git_cache.config.Config: String representation."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.config)
        config = git_cache.config.Config()

        expected_git_cmd = git_cache.config._find_git()  # pylint: disable=protected-access

        expected_config_str = f"""Clone:
 commandtimeout       = 1 hour               (GITCACHE_CLONE_COMMAND_TIMEOUT)
 outputtimeout        = 5 minutes            (GITCACHE_CLONE_OUTPUT_TIMEOUT)
 retries              = 3                    (GITCACHE_CLONE_RETRIES)

Command:
 checkinterval        = 2 seconds            (GITCACHE_COMMAND_CHECK_INTERVAL)
 locktimeout          = 1 hour               (GITCACHE_COMMAND_LOCK_TIMEOUT)
 warniflockedfor      = 10 seconds           (GITCACHE_COMMAND_WARN_IF_LOCKED_FOR)

GC:
 commandtimeout       = 1 hour               (GITCACHE_GC_COMMAND_TIMEOUT)
 outputtimeout        = 5 minutes            (GITCACHE_GC_OUTPUT_TIMEOUT)
 retries              = 3                    (GITCACHE_GC_RETRIES)

LFS:
 commandtimeout       = 1 hour               (GITCACHE_LFS_COMMAND_TIMEOUT)
 outputtimeout        = 5 minutes            (GITCACHE_LFS_OUTPUT_TIMEOUT)
 permirrorstorage     = True                 (GITCACHE_LFS_PER_MIRROR_STORAGE)
 retries              = 3                    (GITCACHE_LFS_RETRIES)

MirrorHandling:
 cleanupafter         = 14 days              (GITCACHE_CLEANUP_AFTER)
 updateinterval       = 0 seconds            (GITCACHE_UPDATE_INTERVAL)

System:
 realgit              = {expected_git_cmd : <20} (GITCACHE_REAL_GIT)

Update:
 commandtimeout       = 1 hour               (GITCACHE_UPDATE_COMMAND_TIMEOUT)
 outputtimeout        = 5 minutes            (GITCACHE_UPDATE_OUTPUT_TIMEOUT)
 retries              = 3                    (GITCACHE_UPDATE_RETRIES)

UrlPatterns:
 excluderegex         =                      (GITCACHE_URLPATTERNS_EXCLUDE_REGEX)
 includeregex         = .*                   (GITCACHE_URLPATTERNS_INCLUDE_REGEX)
"""
        self.assertEqual(str(config), expected_config_str)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
