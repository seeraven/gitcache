#
# Copyright (c) 2026 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.git_mirror module testing normalize_lfs_endpoint()."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase

from git_cache.git_mirror import GitMirror


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheNormalizeLfsEndpointTest(TestCase):
    """Test the :func:`git_cache.git_mirror.GitMirror.normalize_lfs_endpoint` function."""

    def test_normalize_lfs_endpoint(self):
        """git_cache.git_mirror.GitMirror.normalize_lfs_endpoint(): Test the function."""
        expected = "https://github.com/org/repo.git/info/lfs"

        # URL without a .git suffix gets one inserted.
        self.assertEqual(GitMirror.normalize_lfs_endpoint("https://github.com/org/repo"), expected)

        # URL already carrying a .git suffix is not doubled.
        self.assertEqual(GitMirror.normalize_lfs_endpoint("https://github.com/org/repo.git"), expected)

        # Trailing slashes are stripped.
        self.assertEqual(GitMirror.normalize_lfs_endpoint("https://github.com/org/repo/"), expected)
        self.assertEqual(GitMirror.normalize_lfs_endpoint("https://github.com/org/repo.git/"), expected)

        # An already-canonical endpoint is idempotent.
        self.assertEqual(GitMirror.normalize_lfs_endpoint(expected), expected)
        self.assertEqual(GitMirror.normalize_lfs_endpoint("https://github.com/org/repo/info/lfs"), expected)

    def test_get_lfs_url_protocol_scope(self):
        """git_cache.git_mirror.GitMirror.get_lfs_url(): normalize only HTTP(S)/FTP(S)."""
        mirror = GitMirror.__new__(GitMirror)

        # HTTP(S)/FTP(S): force canonical '.git/info/lfs'.
        mirror.url = "https://github.com/org/repo"
        self.assertEqual(mirror.get_lfs_url(), "https://github.com/org/repo.git/info/lfs")

        mirror.url = "ftp://example.com/org/repo"
        self.assertEqual(mirror.get_lfs_url(), "ftp://example.com/org/repo.git/info/lfs")

        # SSH/SCP/file/local paths: keep input unchanged.
        mirror.url = "ssh://git@github.com/org/repo.git"
        self.assertEqual(mirror.get_lfs_url(), "ssh://git@github.com/org/repo.git")

        mirror.url = "git@github.com:org/repo.git"
        self.assertEqual(mirror.get_lfs_url(), "git@github.com:org/repo.git")

        mirror.url = "file:///tmp/repo.git"
        self.assertEqual(mirror.get_lfs_url(), "file:///tmp/repo.git")

        mirror.url = "/tmp/repo.git"
        self.assertEqual(mirror.get_lfs_url(), "/tmp/repo.git")


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
