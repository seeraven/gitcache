#
# Copyright (c) 2026 by Audric Ackermann <audric@getsession.org>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.git_mirror module testing normalize_url()."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase

from git_cache.git_mirror import GitMirror


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheNormalizeUrlTest(TestCase):
    """Test the :func:`git_cache.git_mirror.GitMirror.normalize_url` function."""

    def _assert_normalized(self, url: str, expected: str):
        self.assertEqual(GitMirror.normalize_url(url), expected, url)
        self.assertEqual(GitMirror.normalize_url(expected), expected, expected)

    def test_ssh_user_is_kept(self):
        """git_cache.git_mirror.GitMirror.normalize_url(): Keep the user of ssh:// and scp-style URLs."""
        self._assert_normalized("ssh://git@github.com/org/repo.git", "ssh://git@github.com/org/repo")
        self._assert_normalized("ssh://git@github.com:2222/org/repo.git", "ssh://git@github.com:2222/org/repo")
        self._assert_normalized("ssh://github.com/org/repo.git", "ssh://github.com/org/repo")
        self._assert_normalized("git@github.com:org/repo.git", "git@github.com:org/repo")
        self._assert_normalized("github.com:org/repo.git", "github.com:org/repo")

    def test_ssh_password_is_dropped(self):
        """git_cache.git_mirror.GitMirror.normalize_url(): Drop the password of ssh:// URLs but keep the user."""
        self._assert_normalized("ssh://user:secret@github.com/org/repo.git", "ssh://user@github.com/org/repo")

    def test_other_credentials_are_dropped(self):
        """git_cache.git_mirror.GitMirror.normalize_url(): Drop user and password of http(s), ftp(s) and git URLs."""
        self._assert_normalized("https://user:secret@github.com/org/repo.git", "https://github.com/org/repo")
        self._assert_normalized("https://token@github.com/org/repo", "https://github.com/org/repo")
        self._assert_normalized("http://user:secret@localhost:7698/org/repo.git", "http://localhost:7698/org/repo")
        self._assert_normalized("ftps://user:secret@example.com/repo", "ftps://example.com/repo")
        self._assert_normalized("git://user@github.com/org/repo.git", "git://github.com/org/repo")

    def test_path_is_normalized(self):
        """git_cache.git_mirror.GitMirror.normalize_url(): Strip trailing slashes, '.git' and relative parts."""
        for user in ["", "git@"]:
            self._assert_normalized(f"ssh://{user}github.com/org/repo/", f"ssh://{user}github.com/org/repo")
            self._assert_normalized(f"ssh://{user}github.com/org/repo.git/", f"ssh://{user}github.com/org/repo")
            self._assert_normalized(f"ssh://{user}github.com/org/../org/repo.git", f"ssh://{user}github.com/org/repo")
            self._assert_normalized(f"ssh://{user}github.com/../org/repo.git", f"ssh://{user}github.com/org/repo")
            self._assert_normalized(f"{user}github.com:org/repo/", f"{user}github.com:org/repo")
            self._assert_normalized(f"{user}github.com:org/repo.git/", f"{user}github.com:org/repo")
            self._assert_normalized(f"{user}github.com:org/../org/repo.git", f"{user}github.com:org/repo")
            self._assert_normalized(f"{user}github.com:../org/repo.git", f"{user}github.com:org/repo")

    def test_local_urls_are_untouched(self):
        """git_cache.git_mirror.GitMirror.normalize_url(): Keep file:// URLs and local paths."""
        for url in ("file:///tmp/repo.git", "file:///tmp/a/../repo.git/", "/tmp/repo.git", "../repo"):
            self._assert_normalized(url, url)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
