#
# Copyright (c) 2024 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.commands.helpers module testing resolve_submodule_url()."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase

from git_cache.commands.helpers import resolve_submodule_url


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheResolveSubmoduleUrlTest(TestCase):
    """Test the :func:`git_cache.commands.helpers.resolve_submodule_url` function."""

    def test_urls(self):
        """git_cache.commands.helpers.resolve_submodule_url(): Test URLs with and without protocol."""
        for proto in ["http", "https", "ftp", "ftps", "ssh", "git"]:
            for user in ["", "user@"]:
                for port in ["", ":1234"]:
                    server = f"{proto}://{user}github.com{port}"
                    for repo_url_suffix in ["", "/"]:
                        repo_url = f"{server}/first/second{repo_url_suffix}"
                        for submodule_url_suffix in ["", "/"]:
                            rel_url = f"../sub{submodule_url_suffix}"
                            result = f"{server}/first/sub{submodule_url_suffix}"
                            self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                            rel_url = f"./.././sub{submodule_url_suffix}"
                            self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                            rel_url = f"../../first/sub{submodule_url_suffix}"
                            self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                            rel_url = f"./sub{submodule_url_suffix}"
                            result = f"{server}/first/second/sub{submodule_url_suffix}"
                            self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

        # scp-like URLs
        for user in ["", "user@"]:
            server = f"{user}github.com"
            for repo_url_suffix in ["", "/"]:
                repo_url = f"{server}:first/second{repo_url_suffix}"
                for submodule_url_suffix in ["", "/"]:
                    rel_url = f"../sub{submodule_url_suffix}"
                    result = f"{server}:first/sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                    rel_url = f"./.././sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                    rel_url = f"../../first/sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                    rel_url = f"./sub{submodule_url_suffix}"
                    result = f"{server}:first/second/sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

        # file:// URLs and path specifications
        for proto in ["", "file://"]:
            for repo_url_suffix in ["", "/"]:
                repo_url = f"{proto}/root/path/first/second{repo_url_suffix}"
                for submodule_url_suffix in ["", "/"]:
                    rel_url = f"../sub{submodule_url_suffix}"
                    result = f"{proto}/root/path/first/sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                    rel_url = f"./.././sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                    rel_url = f"../../first/sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))

                    rel_url = f"./sub{submodule_url_suffix}"
                    result = f"{proto}/root/path/first/second/sub{submodule_url_suffix}"
                    self.assertEqual(result, resolve_submodule_url(repo_url, rel_url))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
