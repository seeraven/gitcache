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

        repo_abs_path = os.path.normpath(os.path.join("/tmp", "dummy-dir"))
        database.add("http://dummy/git", repo_abs_path)
        self.assertIn(repo_abs_path, database.get_all())
        self.assertEqual("http://dummy/git", database.get(repo_abs_path)["url"])
        self.assertNotEqual(0, database.get(repo_abs_path)["last-update-time"])
        self.assertEqual(0, database.get(repo_abs_path)["mirror-updates"])
        self.assertEqual(0, database.get(repo_abs_path)["clones"])
        self.assertEqual(0, database.get(repo_abs_path)["updates"])

        # Ensure written database uses relative paths
        with open("/tmp/db", "r", encoding="utf-8") as handle:
            raw_database = json.load(handle)
        self.assertNotIn(repo_abs_path, raw_database)
        self.assertIn("dummy-dir", raw_database)

        database.increment_counter(repo_abs_path, "mirror-updates")
        self.assertEqual(1, database.get(repo_abs_path)["mirror-updates"])
        self.assertEqual(0, database.get(repo_abs_path)["clones"])
        self.assertEqual(0, database.get(repo_abs_path)["updates"])

        database.increment_counter(repo_abs_path, "clones")
        self.assertEqual(1, database.get(repo_abs_path)["mirror-updates"])
        self.assertEqual(1, database.get(repo_abs_path)["clones"])
        self.assertEqual(0, database.get(repo_abs_path)["updates"])

        database.increment_counter(repo_abs_path, "updates")
        self.assertEqual(1, database.get(repo_abs_path)["mirror-updates"])
        self.assertEqual(1, database.get(repo_abs_path)["clones"])
        self.assertEqual(1, database.get(repo_abs_path)["updates"])

        database.clear_counters(repo_abs_path)
        self.assertEqual(0, database.get(repo_abs_path)["mirror-updates"])
        self.assertEqual(0, database.get(repo_abs_path)["clones"])
        self.assertEqual(0, database.get(repo_abs_path)["updates"])

        old_update_time = database.get(repo_abs_path)["last-update-time"]
        time.sleep(0.1)
        database.save_update_time(repo_abs_path)
        time.sleep(0.1)
        self.assertNotEqual(old_update_time, database.get(repo_abs_path)["last-update-time"])
        self.assertTrue(database.get_time_since_last_update(repo_abs_path) < 10.0)
        self.assertNotEqual(0.0, database.get_time_since_last_update(repo_abs_path))

        database.remove(repo_abs_path)
        self.assertNotIn(repo_abs_path, database.get_all())
        self.assertEqual(None, database.get(repo_abs_path))
        self.assertEqual(0.0, database.get_time_since_last_update(repo_abs_path))

        self.assertEqual(None, database.get_url_for_path(repo_abs_path))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
