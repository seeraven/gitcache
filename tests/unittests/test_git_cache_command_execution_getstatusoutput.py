# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.command_execution module testing getstatusoutput()."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import io
import platform
import sys
from unittest import TestCase

from git_cache.command_execution import getstatusoutput


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheGetStatusOutputTest(TestCase):
    """Test the :func:`git_cache.command_execution.getstatusoutput` function."""

    def setUp(self):
        """Set up the test case."""
        # Nose does not provide a sys.stdout.buffer member
        if not hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer = io.BytesIO()

        self.on_windows = platform.system().lower().startswith('win')

    def test_output(self):
        """git_cache.command_execution.getstatusoutput(): Get output of a command."""
        if self.on_windows:
            cmd = ["python", "-c", "print('Hello World')"]
        else:
            cmd = ['echo', 'Hello World']
        return_code, output = getstatusoutput(cmd)
        self.assertEqual(0, return_code)
        self.assertEqual("Hello World", output)

    def test_shell_output(self):
        """git_cache.command_execution.getstatusoutput(): Get output of a command using shell."""
        return_code, output = getstatusoutput('echo Hello World', shell=True)
        self.assertEqual(0, return_code)
        self.assertEqual("Hello World", output)

    def test_return(self):
        """git_cache.command_execution.getstatusoutput(): Get return code."""
        if self.on_windows:
            cmd_true = ['cmd.exe', '/C', 'exit 0']
            cmd_false = ['cmd.exe', '/C', 'exit 1']
        else:
            cmd_true = ['true']
            cmd_false = ['false']
        return_code, output = getstatusoutput(cmd_true)
        self.assertEqual(0, return_code)
        self.assertEqual("", output)

        return_code, output = getstatusoutput(cmd_false)
        self.assertEqual(1, return_code)
        self.assertEqual("", output)

    def test_shell_return(self):
        """git_cache.command_execution.getstatusoutput(): Get return code while using shell."""
        return_code, output = getstatusoutput('exit 0', shell=True)
        self.assertEqual(0, return_code)
        self.assertEqual("", output)

        return_code, output = getstatusoutput('exit 1', shell=True)
        self.assertEqual(1, return_code)
        self.assertEqual("", output)

    def test_command_not_found(self):
        """git_cache.command_execution.getstatusoutput(): Command not found."""
        return_code, output = getstatusoutput('cmd_doesnt_exist')
        self.assertEqual(127, return_code)
        self.assertEqual("", output)

    def test_shell_command_not_found(self):
        """git_cache.command_execution.getstatusoutput(): Command not found using shell."""
        return_code, output = getstatusoutput('cmd_doesnt_exist', shell=True)
        self.assertNotEqual(0, return_code)
        self.assertEqual("", output)

    def test_cwd(self):
        """git_cache.command_execution.getstatusoutput(): Support of cwd."""
        if self.on_windows:
            cmd = ['cmd.exe', '/C', 'echo %CD%']
            cwd = r'C:\Windows'
        else:
            cmd = ['pwd']
            cwd = '/var/log'
        return_code, output = getstatusoutput(cmd, cwd=cwd)
        self.assertEqual(0, return_code)
        self.assertEqual(cwd, output)

    def test_shell_cwd(self):
        """git_cache.command_execution.getstatusoutput(): Support of cwd using shell."""
        if self.on_windows:
            cmd = 'echo %CD%'
            cwd = r'C:\Windows'
        else:
            cmd = ['pwd']
            cwd = '/var/log'
        return_code, output = getstatusoutput(cmd, cwd=cwd, shell=True)
        self.assertEqual(0, return_code)
        self.assertEqual(cwd, output)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
