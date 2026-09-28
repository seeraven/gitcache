#
# Copyright (c) 2026 by Audric Ackermann <audric@getsession.org>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.helpers module testing strip_credentials()."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase

from git_cache.helpers import strip_credentials


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheStripCredentialsTest(TestCase):
    """Test the :func:`git_cache.helpers.strip_credentials` function."""

    def test_http_credentials_are_stripped(self):
        """git_cache.helpers.strip_credentials(): Strip user and password of http(s)/ftp(s) URLs."""
        self.assertEqual(
            strip_credentials("https://user:secret@github.com/org/repo.git"), "https://github.com/org/repo.git"
        )
        self.assertEqual(strip_credentials("https://token@github.com/org/repo"), "https://github.com/org/repo")
        self.assertEqual(
            strip_credentials("http://user:secret@localhost:7698/org/repo"), "http://localhost:7698/org/repo"
        )
        self.assertEqual(strip_credentials("ftps://user:secret@example.com/repo"), "ftps://example.com/repo")
        self.assertEqual(strip_credentials("https://github.com/org/repo.git"), "https://github.com/org/repo.git")

    def test_http_credentials_are_masked(self):
        """git_cache.helpers.strip_credentials(): Mask user and password of http(s) URLs."""
        self.assertEqual(
            strip_credentials("https://user:secret@github.com/org/repo.git", mask=True),
            "https://[MASKED]@github.com/org/repo.git",
        )
        self.assertEqual(
            strip_credentials("https://github.com/org/repo.git", mask=True), "https://github.com/org/repo.git"
        )

    def test_ssh_user_is_kept(self):
        """git_cache.helpers.strip_credentials(): Keep the user of ssh:// and scp-style URLs."""
        for url in (
            "ssh://git@github.com/org/repo.git",
            "ssh://git@github.com:2222/org/repo.git",
            "git@github.com:org/repo.git",
            "git@github.com:org/repo",
            "github.com:org/repo.git",
        ):
            self.assertEqual(strip_credentials(url), url)
            self.assertEqual(strip_credentials(url, mask=True), url)

    def test_local_urls_are_untouched(self):
        """git_cache.helpers.strip_credentials(): Keep file:// URLs and local paths."""
        for url in ("file:///tmp/repo.git", "/tmp/repo.git", "../repo"):
            self.assertEqual(strip_credentials(url), url)
            self.assertEqual(strip_credentials(url, mask=True), url)
