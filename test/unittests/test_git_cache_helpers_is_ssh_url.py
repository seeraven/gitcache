#
# Copyright (c) 2026 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.helpers module testing is_ssh_url()."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase

from git_cache.helpers import is_ssh_url


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheIsSshUrlTest(TestCase):
    """Test the :func:`git_cache.helpers.is_ssh_url` function."""

    def test_ssh_urls(self):
        """git_cache.helpers.is_ssh_url(): Detect ssh:// and scp-style URLs."""
        for url in (
            "git@github.com:org/repo.git",
            "github.com:org/repo.git",
            "ssh://git@github.com/org/repo.git",
            "ssh://github.com:2222/org/repo.git",
        ):
            self.assertTrue(is_ssh_url(url), url)

    def test_other_urls(self):
        """git_cache.helpers.is_ssh_url(): Reject http(s), ftp(s), git://, file:// and local paths."""
        for url in (
            "https://github.com/org/repo.git",
            "https://user:secret@github.com/org/repo.git",
            "ftp://example.com/repo",
            "git://github.com/org/repo.git",
            "file:///tmp/repo.git",
            "/tmp/repo.git",
            "../repo",
        ):
            self.assertFalse(is_ssh_url(url), url)
