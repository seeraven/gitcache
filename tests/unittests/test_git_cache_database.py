# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.database module."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import importlib
import os
from unittest import TestCase

import git_cache.database
import git_cache.global_settings

import mock


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def mockenv(**envvars):
    """Set up a temporary new environment."""
    return mock.patch.dict(os.environ, envvars)


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheDatabaseTest(TestCase):
    """Test the :class:`git_cache.database.Database` class."""

    def setUp(self):
        """Set up the test case."""
        if os.path.exists("/tmp/db"):
            os.unlink("/tmp/db")
            os.unlink("/tmp/db.lock")

    def tearDown(self):
        """Tear down the test case."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.database)

        if os.path.exists("/tmp/db"):
            os.unlink("/tmp/db")
            os.unlink("/tmp/db.lock")

    @mockenv(GITCACHE_DIR="/tmp")
    def test_database(self):
        """git_cache.database.Database: Test database."""
        importlib.reload(git_cache.global_settings)
        importlib.reload(git_cache.database)

        database = git_cache.database.Database()
        self.assertFalse(database.database)

        database.add("http://dummy/git", "dummy-dir")
        self.assertIn("dummy-dir", database.get_all())
        self.assertEqual("http://dummy/git", database.get("dummy-dir")["url"])
        self.assertNotEqual(0, database.get("dummy-dir")["last-update-time"])
        self.assertEqual(0, database.get("dummy-dir")["mirror-updates"])
        self.assertEqual(0, database.get("dummy-dir")["clones"])
        self.assertEqual(0, database.get("dummy-dir")["updates"])

        database.increment_counter("dummy-dir", "mirror-updates")
        self.assertEqual(1, database.get("dummy-dir")["mirror-updates"])
        self.assertEqual(0, database.get("dummy-dir")["clones"])
        self.assertEqual(0, database.get("dummy-dir")["updates"])

        database.increment_counter("dummy-dir", "clones")
        self.assertEqual(1, database.get("dummy-dir")["mirror-updates"])
        self.assertEqual(1, database.get("dummy-dir")["clones"])
        self.assertEqual(0, database.get("dummy-dir")["updates"])

        database.increment_counter("dummy-dir", "updates")
        self.assertEqual(1, database.get("dummy-dir")["mirror-updates"])
        self.assertEqual(1, database.get("dummy-dir")["clones"])
        self.assertEqual(1, database.get("dummy-dir")["updates"])

        database.clear_counters("dummy-dir")
        self.assertEqual(0, database.get("dummy-dir")["mirror-updates"])
        self.assertEqual(0, database.get("dummy-dir")["clones"])
        self.assertEqual(0, database.get("dummy-dir")["updates"])

        old_update_time = database.get("dummy-dir")["last-update-time"]
        database.save_update_time("dummy-dir")
        self.assertNotEqual(old_update_time, database.get("dummy-dir")["last-update-time"])
        self.assertTrue(database.get_time_since_last_update("dummy-dir") < 10.0)
        self.assertNotEqual(0.0, database.get_time_since_last_update("dummy-dir"))

        # self.assertTrue(database.update_time_reached("dummy-dir"))
        # self.assertFalse(database.cleanup_time_reached("dummy-dir"))

        database.remove("dummy-dir")
        self.assertNotIn("dummy-dir", database.get_all())
        self.assertEqual(None, database.get("dummy-dir"))
        self.assertEqual(0.0, database.get_time_since_last_update("dummy-dir"))

    # @mockenv(GITCACHE_DIR="/tmp",
    #          GITCACHE_UPDATE_INTERVAL="-1")
    # def test_negative_update_interval(self):
    #     """git_cache.database.Database: Test negative update interval."""
    #     importlib.reload(git_cache.global_settings)
    #     importlib.reload(git_cache.settings)
    #     importlib.reload(git_cache.database)

    #     database = git_cache.database.Database()
    #     database.add("http://dummy/git", "dummy-dir")
    #     self.assertFalse(database.update_time_reached("dummy-dir"))

    # @mockenv(GITCACHE_DIR="/tmp",
    #          GITCACHE_UPDATE_INTERVAL="1000")
    # def test_large_update_interval(self):
    #     """git_cache.database.Database: Test large update interval."""
    #     importlib.reload(git_cache.global_settings)
    #     importlib.reload(git_cache.settings)
    #     importlib.reload(git_cache.database)

    #     database = git_cache.database.Database()
    #     database.add("http://dummy/git", "dummy-dir")
    #     self.assertFalse(database.update_time_reached("dummy-dir"))

    #     database.database["dummy-dir"]["last-update-time"] -= 2000
    #     # pylint: disable=protected-access
    #     database._save()
    #     self.assertTrue(database.update_time_reached("dummy-dir"))
    #     self.assertFalse(database.update_time_reached("non-existant"))

    # @mockenv(GITCACHE_DIR="/tmp",
    #          GITCACHE_CLEANUP_INTERVAL="1000")
    # def test_cleanup_time_reached(self):
    #     """git_cache.database.Database: Test cleanup time."""
    #     importlib.reload(git_cache.global_settings)
    #     importlib.reload(git_cache.settings)
    #     importlib.reload(git_cache.database)

    #     database = git_cache.database.Database()
    #     database.add("http://dummy/git", "dummy-dir")
    #     self.assertFalse(database.cleanup_time_reached("dummy-dir"))

    #     database.database["dummy-dir"]["last-update-time"] -= 2000
    #     # pylint: disable=protected-access
    #     database._save()
    #     self.assertTrue(database.cleanup_time_reached("dummy-dir"))
    #     self.assertFalse(database.cleanup_time_reached("non-existant"))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
