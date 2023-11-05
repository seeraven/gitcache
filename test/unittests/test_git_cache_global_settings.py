# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.global_settings module."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import os
from unittest import TestCase

import git_cache.global_settings


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheSettingsTest(TestCase):
    """Test the :class:`git_cache.settings` module."""

    def test_settings(self):
        """git_cache.settings: Valid entries."""
        self.assertEqual(
            git_cache.global_settings.GITCACHE_DIR,
            os.getenv("GITCACHE_DIR", os.path.join(os.getenv("HOME", "/"), ".gitcache")),
        )
        self.assertEqual(
            git_cache.global_settings.GITCACHE_DB, os.path.join(git_cache.global_settings.GITCACHE_DIR, "db")
        )
        self.assertEqual(
            git_cache.global_settings.GITCACHE_DB_LOCK, os.path.join(git_cache.global_settings.GITCACHE_DIR, "db.lock")
        )
        self.assertEqual(git_cache.global_settings.GITCACHE_LOGLEVEL, os.getenv("GITCACHE_LOGLEVEL", "INFO"))
        self.assertEqual(
            git_cache.global_settings.GITCACHE_LOGFORMAT, os.getenv("GITCACHE_LOGFORMAT", "%(asctime)s %(message)s")
        )


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
