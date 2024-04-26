#
# Copyright (c) 2024 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.git_mirror module testing get_mirror_path()."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import os
from unittest import TestCase

from git_cache.git_mirror import GitMirror
from git_cache.global_settings import GITCACHE_DIR


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheGetMirrorPathTest(TestCase):
    """Test the :func:`git_cache.git_mirror.GitMirror.get_mirror_path` function."""

    def test_get_mirror_path(self):
        """git_cache.git_mirror.GitMirror.get_mirror_path(): Test the function."""
        for proto in ["http", "https", "ftp", "ftps", "ssh", "git"]:
            for user in ["", "user@"]:
                for port in ["", ":1234"]:
                    server = f"{proto}://{user}github.com{port}"
                    mirror_base = os.path.join(GITCACHE_DIR, "mirrors", f"github.com{port}".replace(":", "_"))
                    for repo_url_suffix in ["", "/"]:
                        # trailing slash is stripped
                        path = GitMirror.get_mirror_path(f"{server}/repo{repo_url_suffix}")
                        self.assertEqual(path, os.path.join(mirror_base, "repo"))

                        # .git suffix is stripped too
                        path = GitMirror.get_mirror_path(f"{server}/repo.git{repo_url_suffix}")
                        self.assertEqual(path, os.path.join(mirror_base, "repo"))

                        # paths are normalized
                        path = GitMirror.get_mirror_path(f"{server}/somewhere/../repo.git{repo_url_suffix}")
                        self.assertEqual(path, os.path.join(mirror_base, "repo"))

                        # and no escaping possible
                        path = GitMirror.get_mirror_path(f"{server}/.././../repo.git{repo_url_suffix}")
                        self.assertEqual(path, os.path.join(mirror_base, "repo"))

        # scp-like urls
        for user in ["", "user@"]:
            server = f"{user}github.com"
            mirror_base = os.path.join(GITCACHE_DIR, "mirrors", "github.com")
            for repo_url_suffix in ["", "/"]:
                # trailing slash is stripped
                path = GitMirror.get_mirror_path(f"{server}:repo{repo_url_suffix}")
                self.assertEqual(path, os.path.join(mirror_base, "repo"))

                # .git suffix is stripped too
                path = GitMirror.get_mirror_path(f"{server}:repo.git{repo_url_suffix}")
                self.assertEqual(path, os.path.join(mirror_base, "repo"))

                # paths are normalized
                path = GitMirror.get_mirror_path(f"{server}:somewhere/../repo.git{repo_url_suffix}")
                self.assertEqual(path, os.path.join(mirror_base, "repo"))

                # and no escaping possible
                path = GitMirror.get_mirror_path(f"{server}:.././../repo.git{repo_url_suffix}")
                self.assertEqual(path, os.path.join(mirror_base, "repo"))

        # file:// urls
        path = GitMirror.get_mirror_path("file:///somewhere/a/file")
        self.assertEqual(path, "")

        path = GitMirror.get_mirror_path(f"file://{GITCACHE_DIR}/file")
        self.assertEqual(path, f"{GITCACHE_DIR}/file")

        path = GitMirror.get_mirror_path(f"file://{GITCACHE_DIR}/a/../file")
        self.assertEqual(path, f"{GITCACHE_DIR}/file")

        path = GitMirror.get_mirror_path(f"file://{GITCACHE_DIR}/../file")
        self.assertEqual(path, "")

        # files
        path = GitMirror.get_mirror_path(os.path.join(GITCACHE_DIR, "config"))
        self.assertEqual(path, os.path.join(GITCACHE_DIR, "config"))

        path = GitMirror.get_mirror_path(os.path.join(GITCACHE_DIR, "a", "..", "config"))
        self.assertEqual(path, os.path.join(GITCACHE_DIR, "config"))

        path = GitMirror.get_mirror_path(os.path.join(GITCACHE_DIR, "..", "file"))
        self.assertEqual(path, None)

        path = GitMirror.get_mirror_path(__file__)
        self.assertEqual(path, "")


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
