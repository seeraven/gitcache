# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.command_execution module testing simple_call_command()."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import io
import platform
import sys
from unittest import TestCase

from git_cache.command_execution import simple_call_command


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheSimpleCallCommandTest(TestCase):
    """Test the :func:`git_cache.command_execution.simple_call_command` function."""

    def setUp(self):
        """Set up the test case."""
        # Nose does not provide a sys.stdout.buffer member
        if not hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer = io.BytesIO()

        self.on_windows = platform.system().lower().startswith("win")

    def test_return(self):
        """git_cache.command_execution.simple_call_command(): Get return code."""
        if self.on_windows:
            cmd_true = ["cmd.exe", "/C", "exit 0"]
            cmd_false = ["cmd.exe", "/C", "exit 1"]
        else:
            cmd_true = ["true"]
            cmd_false = ["false"]
        self.assertEqual(0, simple_call_command(cmd_true))
        self.assertEqual(1, simple_call_command(cmd_false))

    def test_shell_return(self):
        """git_cache.command_execution.simple_call_command(): Get return code using shell."""
        self.assertEqual(0, simple_call_command("exit 0", shell=True))
        self.assertEqual(1, simple_call_command("exit 1", shell=True))

    def test_command_not_found(self):
        """git_cache.command_execution.simple_call_command(): Command not found."""
        self.assertEqual(127, simple_call_command("cmd_doesnt_exist"))

    def test_shell_command_not_found(self):
        """git_cache.command_execution.simple_call_command(): Command not found using shell."""
        self.assertNotEqual(0, simple_call_command("cmd_doesnt_exist", shell=True))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
