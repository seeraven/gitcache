# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.command_execution module testing call_command_retry()."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import io
import os
import platform
import sys
from unittest import TestCase

from git_cache.command_execution import call_command_retry


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheCallCommandRetryTest(TestCase):
    """Test the :func:`git_cache.command_execution.call_command_retry` function."""

    def setUp(self):
        """Set up the test case."""
        # Nose does not provide a sys.stdout.buffer member
        if not hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer = io.BytesIO()

        self.on_windows = platform.system().lower().startswith("win")

    def test_return(self):
        """git_cache.command_execution.call_command_retry(): Get return code."""
        if self.on_windows:
            cmd_true = ["cmd.exe", "/C", "exit 0"]
            cmd_false = ["cmd.exe", "/C", "exit 1"]
        else:
            cmd_true = ["true"]
            cmd_false = ["false"]
        return_code, stdout_buffer, stderr_buffer = call_command_retry(cmd_true, 3)
        self.assertEqual(0, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

        return_code, stdout_buffer, stderr_buffer = call_command_retry(cmd_false, 3)
        self.assertEqual(1, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

    def test_shell_return(self):
        """git_cache.command_execution.call_command_retry(): Get return code using shell."""
        return_code, stdout_buffer, stderr_buffer = call_command_retry("exit 0", 3, shell=True)
        self.assertEqual(0, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

        return_code, stdout_buffer, stderr_buffer = call_command_retry("exit 1", 3, shell=True)
        self.assertEqual(1, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

    def test_command_not_found(self):
        """git_cache.command_execution.call_command_retry(): Command not found."""
        return_code, stdout_buffer, stderr_buffer = call_command_retry("cmd_doesnt_exist", 3)
        self.assertEqual(127, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

    def test_shell_command_not_found(self):
        """git_cache.command_execution.call_command_retry(): Command not found using shell."""
        return_code, stdout_buffer, _ = call_command_retry("cmd_doesnt_exist", 3, shell=True)
        self.assertNotEqual(0, return_code)
        if not self.on_windows:
            self.assertEqual(b"", stdout_buffer)
        # self.assertEqual(b'', stderr_buffer)

    def test_cwd(self):
        """git_cache.command_execution.call_command_retry(): Support of cwd."""
        if self.on_windows:
            cmd = ["cmd.exe", "/C", "echo %CD%"]
            cwd = r"C:\Windows"
        else:
            cmd = ["pwd"]
            cwd = "/var/log"
        return_code, stdout_buffer, _ = call_command_retry(cmd, 3, cwd=cwd)
        self.assertEqual(0, return_code)
        self.assertIn(cwd, stdout_buffer.decode().strip())

    def test_shell_cwd(self):
        """git_cache.command_execution.call_command_retry(): Support of cwd using shell."""
        if self.on_windows:
            cmd = "echo %CD%"
            cwd = r"C:\Windows"
        else:
            cmd = ["pwd"]
            cwd = "/var/log"
        return_code, stdout_buffer, _ = call_command_retry(cmd, 3, cwd=cwd, shell=True)
        self.assertEqual(0, return_code)
        self.assertIn(cwd, stdout_buffer.decode().strip())

    def test_timeout(self):
        """git_cache.command_execution.call_command_retry(): Command timeout."""
        if self.on_windows:
            cmd = ["cmd.exe", "/C", "ping -n 3 127.0.0.1 >nul"]
        else:
            cmd = ["sleep", "2s"]
        return_code, stdout_buffer, stderr_buffer = call_command_retry(cmd, 3, command_timeout=1)
        self.assertEqual(-1000, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

    def test_shell_timeout(self):
        """git_cache.command_execution.call_command_retry(): Command timeout using shell."""
        if self.on_windows:
            cmd = "ping -n 3 127.0.0.1 >nul"
        else:
            cmd = "sleep 2s"
        return_code, stdout_buffer, stderr_buffer = call_command_retry(cmd, 3, shell=True, command_timeout=1)
        self.assertEqual(-1000, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

    def test_shell_output_timeout(self):
        """git_cache.command_execution.call_command_retry(): Output timeout using shell."""
        if self.on_windows:
            cmd = "echo a & ping -n 2 127.0.0.1 >nul & echo b & "
            cmd += "ping -n 4 127.0.0.1 >nul & echo c"
        else:
            cmd = "echo a; sleep 1s; echo b; sleep 3s; echo c"
        return_code, stdout_buffer, stderr_buffer = call_command_retry(cmd, 3, shell=True, output_timeout=2)
        self.assertEqual(-2000, return_code)
        # On Windows we seem to not receive the partial output
        if not self.on_windows:
            self.assertEqual(b"a\r\nb\r\n", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)

    def test_remove_dir(self):
        """git_cache.command_execution.call_command_retry(): Remove directory on error."""
        if self.on_windows:
            dir_name = "C:\\tmp\\dummydir"
            cmd = ["cmd.exe", "/C", "exit 1"]
        else:
            dir_name = "/tmp/dummydir"
            cmd = ["false"]
        os.makedirs(dir_name, exist_ok=True)
        return_code, stdout_buffer, stderr_buffer = call_command_retry(cmd, 3, shell=True, remove_dir=dir_name)
        self.assertNotEqual(0, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)
        self.assertFalse(os.path.exists(dir_name))

    def test_shell_remove_dir(self):
        """git_cache.command_execution.call_command_retry(): Remove directory on error in shell."""
        if self.on_windows:
            dir_name = "C:\\tmp\\dummydir"
            cmd = f"mkdir {dir_name} & exit 1"
        else:
            dir_name = "/tmp/dummydir"
            cmd = f"mkdir {dir_name}; false"
        return_code, stdout_buffer, stderr_buffer = call_command_retry(cmd, 3, shell=True, remove_dir=dir_name)
        self.assertNotEqual(0, return_code)
        self.assertEqual(b"", stdout_buffer)
        self.assertEqual(b"", stderr_buffer)
        self.assertFalse(os.path.exists(dir_name))

    def test_abort_pattern(self):
        """git_cache.command_execution.call_command_retry(): Abort on pattern."""
        if self.on_windows:
            cmd = ["cmd.exe", "/C", "echo a & echo abort_marker & exit 1"]
        else:
            cmd = ["/bin/sh", "-c", "echo a; echo abort_marker; exit 1"]
        return_code, stdout_buffer, _ = call_command_retry(cmd, 3, abort_on_pattern=b"abort_marker")
        self.assertEqual(-3000, return_code)
        self.assertIn(b"abort_marker", stdout_buffer)

        return_code, stdout_buffer, _ = call_command_retry(cmd, 3, abort_on_pattern=b"abort_markerddddd")
        self.assertEqual(1, return_code)
        self.assertIn(b"abort_marker", stdout_buffer)

    def test_shell_abort_pattern(self):
        """git_cache.command_execution.call_command_retry(): Abort on pattern using shell."""
        if self.on_windows:
            cmd = "echo a & echo abort_marker & exit 1"
        else:
            cmd = "echo a; echo abort_marker; exit 1"
        return_code, stdout_buffer, _ = call_command_retry(cmd, 3, shell=True, abort_on_pattern=b"abort_marker")
        self.assertEqual(-3000, return_code)
        self.assertIn(b"abort_marker", stdout_buffer)

        return_code, stdout_buffer, _ = call_command_retry(cmd, 3, shell=True, abort_on_pattern=b"abort_markerddddd")
        self.assertEqual(1, return_code)
        self.assertIn(b"abort_marker", stdout_buffer)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
