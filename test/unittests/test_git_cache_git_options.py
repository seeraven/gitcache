# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.git_options module."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import os
from unittest import TestCase

import git_cache.git_options
from git_cache.config import find_git


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheGitOptionsTest(TestCase):
    """Test the :class:`git_cache.git_options.GitOptions` class."""

    def test_bail_out(self):
        """git_cache.git_options.GitOptions: Test bail out detection."""
        args = ["--help"]
        git_options = git_cache.git_options.GitOptions(args)
        self.assertTrue(git_options.has_bail_out())

        args = ["--exec-path"]
        git_options = git_cache.git_options.GitOptions(args)
        self.assertTrue(git_options.has_bail_out())

        args = ["--exec-path=/usr/bin/git"]
        git_options = git_cache.git_options.GitOptions(args)
        self.assertFalse(git_options.has_bail_out())

    def test_get_command(self):
        """git_cache.git_options.GitOptions: Test command extraction."""
        args = ["lfs", "fetch"]
        git_options = git_cache.git_options.GitOptions(args)
        self.assertEqual("lfs_fetch", git_options.get_command())

        args = ["fetch"]
        git_options = git_cache.git_options.GitOptions(args)
        self.assertEqual("fetch", git_options.get_command())

        args = ["unknown"]
        git_options = git_cache.git_options.GitOptions(args)
        self.assertEqual("unknown", git_options.get_command())

    def test_real_git(self):
        """git_cache.git_options.GitOptions: Test real git command setup."""
        args = ["-C", "1", "-c", "user.email=something", "--git-dir=here"]
        git_options = git_cache.git_options.GitOptions(args)
        self.assertListEqual(
            [find_git(), "-C", "1", "-c", "user.email=something", "--git-dir=here"],
            git_options.get_real_git_with_options(),
        )

    def test_run_path(self):
        """git_cache.git_options.GitOptions: Test run_path extraction."""
        args = ["-C", "1", "-C", "2", "-C3"]
        git_options = git_cache.git_options.GitOptions(args)
        run_path_list = git_options.get_global_group_values("run_path")
        self.assertEqual(2, len(run_path_list))
        self.assertEqual("1", run_path_list[0])
        self.assertEqual("2", run_path_list[1])

        abs_run_path = git_options.get_run_path()
        self.assertEqual(os.path.abspath(os.path.join("1", "2")), abs_run_path)

        args = ["fetch"]
        git_options = git_cache.git_options.GitOptions(args)
        abs_run_path = git_options.get_run_path()
        self.assertEqual(os.path.abspath(os.path.curdir), abs_run_path)

    def test_parse(self):
        """git_cache.git_options.GitOptions: Test parsing commands."""
        args = "-C 1 fetch --upload-pack=pack -j5 --depth 2 -o 3 first scnd --filter flt".split(" ")
        git_options = git_cache.git_options.GitOptions(args)
        self.assertEqual(2, len(git_options.global_options))
        self.assertEqual("-C", git_options.global_options[0])
        self.assertEqual("1", git_options.global_options[1])

        self.assertEqual("fetch", git_options.command)

        self.assertEqual(8, len(git_options.command_options))
        self.assertEqual("--upload-pack=pack", git_options.command_options[0])
        self.assertEqual("-j5", git_options.command_options[1])
        self.assertEqual("--depth", git_options.command_options[2])
        self.assertEqual("2", git_options.command_options[3])
        self.assertEqual("-o", git_options.command_options[4])
        self.assertEqual("3", git_options.command_options[5])
        self.assertEqual("--filter", git_options.command_options[6])
        self.assertEqual("flt", git_options.command_options[7])

        self.assertEqual(2, len(git_options.command_args))
        self.assertEqual("first", git_options.command_args[0])
        self.assertEqual("scnd", git_options.command_args[1])

    def test_separator(self):
        """git_cache.git_options.GitOptions: Test arguments with the '--' separator."""
        args = "-C 1 fetch --upload-pack=pack -- first scnd --filter flt".split(" ")
        git_options = git_cache.git_options.GitOptions(args)
        self.assertEqual(2, len(git_options.global_options))
        self.assertEqual("-C", git_options.global_options[0])
        self.assertEqual("1", git_options.global_options[1])

        self.assertEqual("fetch", git_options.command)

        self.assertEqual(1, len(git_options.command_options))
        self.assertEqual("--upload-pack=pack", git_options.command_options[0])

        self.assertEqual(4, len(git_options.command_args))
        self.assertEqual("first", git_options.command_args[0])
        self.assertEqual("scnd", git_options.command_args[1])
        self.assertEqual("--filter", git_options.command_args[2])
        self.assertEqual("flt", git_options.command_args[3])

    def test_subcommand(self):
        """git_cache.git_options.GitOptions: Test options in-between subcommand."""
        args = "submodule --quiet status".split(" ")
        git_options = git_cache.git_options.GitOptions(args)
        self.assertEqual("submodule_status", git_options.command)
        self.assertEqual(1, len(git_options.command_options))
        self.assertEqual("--quiet", git_options.command_options[0])

        # This command makes no sense but tests the stability of the parser:
        args = "submodule".split(" ")
        git_options = git_cache.git_options.GitOptions(args)
        self.assertEqual("submodule", git_options.command)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
