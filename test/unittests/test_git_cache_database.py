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
import json
import os
import time
from unittest import TestCase

import mock

import git_cache.database
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

        database.add("http://dummy/git", "/tmp/dummy-dir")
        self.assertIn("/tmp/dummy-dir", database.get_all())
        self.assertEqual("http://dummy/git", database.get("/tmp/dummy-dir")["url"])
        self.assertNotEqual(0, database.get("/tmp/dummy-dir")["last-update-time"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["mirror-updates"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["clones"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["updates"])

        # Ensure written database uses relative paths
        with open("/tmp/db", "r", encoding="utf-8") as handle:
            raw_database = json.load(handle)
        self.assertNotIn("/tmp/dummy-dir", raw_database)
        self.assertIn("dummy-dir", raw_database)

        database.increment_counter("/tmp/dummy-dir", "mirror-updates")
        self.assertEqual(1, database.get("/tmp/dummy-dir")["mirror-updates"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["clones"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["updates"])

        database.increment_counter("/tmp/dummy-dir", "clones")
        self.assertEqual(1, database.get("/tmp/dummy-dir")["mirror-updates"])
        self.assertEqual(1, database.get("/tmp/dummy-dir")["clones"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["updates"])

        database.increment_counter("/tmp/dummy-dir", "updates")
        self.assertEqual(1, database.get("/tmp/dummy-dir")["mirror-updates"])
        self.assertEqual(1, database.get("/tmp/dummy-dir")["clones"])
        self.assertEqual(1, database.get("/tmp/dummy-dir")["updates"])

        database.clear_counters("/tmp/dummy-dir")
        self.assertEqual(0, database.get("/tmp/dummy-dir")["mirror-updates"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["clones"])
        self.assertEqual(0, database.get("/tmp/dummy-dir")["updates"])

        old_update_time = database.get("/tmp/dummy-dir")["last-update-time"]
        time.sleep(0.1)
        database.save_update_time("/tmp/dummy-dir")
        time.sleep(0.1)
        self.assertNotEqual(old_update_time, database.get("/tmp/dummy-dir")["last-update-time"])
        self.assertTrue(database.get_time_since_last_update("/tmp/dummy-dir") < 10.0)
        self.assertNotEqual(0.0, database.get_time_since_last_update("/tmp/dummy-dir"))

        # self.assertTrue(database.update_time_reached("/tmp/dummy-dir"))
        # self.assertFalse(database.cleanup_time_reached("/tmp/dummy-dir"))

        database.remove("/tmp/dummy-dir")
        self.assertNotIn("/tmp/dummy-dir", database.get_all())
        self.assertEqual(None, database.get("/tmp/dummy-dir"))
        self.assertEqual(0.0, database.get_time_since_last_update("/tmp/dummy-dir"))

        self.assertEqual(None, database.get_url_for_path("/tmp/dummy-dir"))

    # @mockenv(GITCACHE_DIR="/tmp",
    #          GITCACHE_UPDATE_INTERVAL="-1")
    # def test_negative_update_interval(self):
    #     """git_cache.database.Database: Test negative update interval."""
    #     importlib.reload(git_cache.global_settings)
    #     importlib.reload(git_cache.settings)
    #     importlib.reload(git_cache.database)

    #     database = git_cache.database.Database()
    #     database.add("http://dummy/git", "/tmp/dummy-dir")
    #     self.assertFalse(database.update_time_reached("/tmp/dummy-dir"))

    # @mockenv(GITCACHE_DIR="/tmp",
    #          GITCACHE_UPDATE_INTERVAL="1000")
    # def test_large_update_interval(self):
    #     """git_cache.database.Database: Test large update interval."""
    #     importlib.reload(git_cache.global_settings)
    #     importlib.reload(git_cache.settings)
    #     importlib.reload(git_cache.database)

    #     database = git_cache.database.Database()
    #     database.add("http://dummy/git", "/tmp/dummy-dir")
    #     self.assertFalse(database.update_time_reached("/tmp/dummy-dir"))

    #     database.database["/tmp/dummy-dir"]["last-update-time"] -= 2000
    #     # pylint: disable=protected-access
    #     database._save()
    #     self.assertTrue(database.update_time_reached("/tmp/dummy-dir"))
    #     self.assertFalse(database.update_time_reached("non-existant"))

    # @mockenv(GITCACHE_DIR="/tmp",
    #          GITCACHE_CLEANUP_INTERVAL="1000")
    # def test_cleanup_time_reached(self):
    #     """git_cache.database.Database: Test cleanup time."""
    #     importlib.reload(git_cache.global_settings)
    #     importlib.reload(git_cache.settings)
    #     importlib.reload(git_cache.database)

    #     database = git_cache.database.Database()
    #     database.add("http://dummy/git", "/tmp/dummy-dir")
    #     self.assertFalse(database.cleanup_time_reached("/tmp/dummy-dir"))

    #     database.database["/tmp/dummy-dir"]["last-update-time"] -= 2000
    #     # pylint: disable=protected-access
    #     database._save()
    #     self.assertTrue(database.cleanup_time_reached("/tmp/dummy-dir"))
    #     self.assertFalse(database.cleanup_time_reached("non-existant"))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
