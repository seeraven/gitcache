#
# Copyright (c) 2026 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.helpers module testing get_user()."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase

from git_cache.helpers import get_user


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheGetUserTest(TestCase):
    """Test the :func:`git_cache.helpers.get_user` function."""

    def test_urls_with_user(self):
        """git_cache.helpers.get_user(): Return the user of URLs carrying one."""
        self.assertEqual(get_user("git@github.com:org/repo.git"), "git")
        self.assertEqual(get_user("ssh://git@github.com/org/repo.git"), "git")
        self.assertEqual(get_user("ssh://git@github.com:2222/org/repo.git"), "git")
        self.assertEqual(get_user("ssh://user:secret@github.com/org/repo.git"), "user")
        self.assertEqual(get_user("https://user:secret@github.com/org/repo.git"), "user")
        self.assertEqual(get_user("https://token@github.com/org/repo"), "token")

    def test_urls_without_user(self):
        """git_cache.helpers.get_user(): Return None for URLs without a user."""
        for url in (
            "github.com:org/repo.git",
            "ssh://github.com/org/repo.git",
            "https://github.com/org/repo.git",
            "file:///tmp/repo.git",
            "/tmp/repo.git",
        ):
            self.assertIsNone(get_user(url), url)
