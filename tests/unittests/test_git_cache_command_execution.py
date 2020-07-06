# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.command_execution module."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import io
import os
import sys
from unittest import TestCase

from git_cache.command_execution import call_command, call_command_retry, \
    getstatusoutput, pretty_call_command_retry, simple_call_command


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class GitCacheCommandExecutionTest(TestCase):
    """Test the :class:`git_cache.command_execution` module."""

    def setUp(self):
        """Set up the test case."""
        # Nose does not provide a sys.stdout.buffer member
        if not hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer = io.BytesIO()

    def test_call_command_valid(self):
        """git_cache.command_execution.call_command(): Valid command."""
        return_code, stdout_buffer, stderr_buffer = call_command("true")
        self.assertEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)

    def test_call_command_timeout(self):
        """git_cache.command_execution.call_command(): Command timeout."""
        return_code, stdout_buffer, stderr_buffer = call_command("sleep 2s",
                                                                 command_timeout=1)
        self.assertEqual(-1000, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)

    def test_call_command_otimeout(self):
        """git_cache.command_execution.call_command(): Output timeout."""
        return_code, stdout_buffer, stderr_buffer = call_command(
            "echo a; sleep 1s; echo b; sleep 3s; echo c",
            output_timeout=2)
        self.assertEqual(-2000, return_code)
        self.assertEqual(b'a\r\nb\r\n', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)

    def test_call_command_invalid(self):
        """git_cache.command_execution.call_command(): Invalid command."""
        return_code, stdout_buffer, stderr_buffer = call_command("cmd_doesnt_exist")
        self.assertNotEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertIn(b'command not found', stderr_buffer)

    def test_call_command_retcode(self):
        """git_cache.command_execution.call_command(): Correct return code."""
        return_code, stdout_buffer, stderr_buffer = call_command("exit 12")
        self.assertEqual(12, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)

    def test_retry_valid(self):
        """git_cache.command_execution.call_command_retry(): Valid command."""
        return_code, stdout_buffer, stderr_buffer = call_command_retry("true", 3)
        self.assertEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)

    def test_retry_invalid(self):
        """git_cache.command_execution.call_command_retry(): Invalid command."""
        return_code, stdout_buffer, stderr_buffer = call_command_retry("cmd_doesnt_exist", 1)
        self.assertNotEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertIn(b'command not found', stderr_buffer)

    def test_retry_remove_dir(self):
        """git_cache.command_execution.call_command_retry(): Remove directory on error."""
        return_code, stdout_buffer, stderr_buffer = call_command_retry("mkdir /tmp/dummydir; false",
                                                                       3,
                                                                       remove_dir="/tmp/dummydir")
        self.assertNotEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)
        self.assertFalse(os.path.exists("/tmp/dummydir"))

    def test_retry_abort_pattern(self):
        """git_cache.command_execution.call_command_retry(): Abort on pattern."""
        return_code, stdout_buffer, stderr_buffer = call_command_retry(
            "cmd_doesnt_exist", 3, abort_on_pattern=b'command not found')
        self.assertEqual(-3000, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertIn(b'command not found', stderr_buffer)

        return_code, stdout_buffer, stderr_buffer = call_command_retry(
            "cmd_doesnt_exist", 3, abort_on_pattern=b'command not founddddd')
        self.assertNotEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertIn(b'command not found', stderr_buffer)

    def test_pretty_retry_valid(self):
        """git_cache.command_execution.pretty_call_command_retry(): Valid command."""
        return_code, stdout_buffer, stderr_buffer = pretty_call_command_retry(
            "Valid command", "", "true", 3)
        self.assertEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)

    def test_pretty_retry_invalid(self):
        """git_cache.command_execution.pretty_call_command_retry(): Invalid command."""
        return_code, stdout_buffer, stderr_buffer = pretty_call_command_retry(
            "Invalid command", "", "cmd_doesnt_exist", 1)
        self.assertNotEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertIn(b'command not found', stderr_buffer)

    def test_pretty_retry_remove_dir(self):
        """git_cache.command_execution.pretty_call_command_retry(): Remove directory on error."""
        return_code, stdout_buffer, stderr_buffer = pretty_call_command_retry(
            "Retry remove directory", "", "mkdir /tmp/dummydir; false",
            3,
            remove_dir="/tmp/dummydir")
        self.assertNotEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertEqual(b'', stderr_buffer)
        self.assertFalse(os.path.exists("/tmp/dummydir"))

    def test_pretty_retry_abort_pattern(self):
        """git_cache.command_execution.pretty_call_command_retry(): Abort on pattern."""
        return_code, stdout_buffer, stderr_buffer = pretty_call_command_retry(
            "Abort on pattern", "Abort pattern", "cmd_doesnt_exist",
            3, abort_on_pattern=b'command not found')
        self.assertEqual(-3000, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertIn(b'command not found', stderr_buffer)

        return_code, stdout_buffer, stderr_buffer = pretty_call_command_retry(
            "Abort on pattern", "Abort pattern", "cmd_doesnt_exist",
            3, abort_on_pattern=b'command not founddddd')
        self.assertNotEqual(0, return_code)
        self.assertEqual(b'', stdout_buffer)
        self.assertIn(b'command not found', stderr_buffer)

    def test_simple_call_valid(self):
        """git_cache.command_execution.simple_call_command(): Valid command."""
        self.assertEqual(0, simple_call_command('true'.split(' ')))

    def test_simple_call_invalid(self):
        """git_cache.command_execution.simple_call_command(): Invalid command."""
        self.assertEqual(1, simple_call_command('false'.split(' ')))

    def test_simple_call_return(self):
        """git_cache.command_execution.simple_call_command(): Return code."""
        self.assertEqual(12, simple_call_command('exit 12'.split(' ')))

    def test_getstatusoutput_valid(self):
        """git_cache.command_execution.getstatusoutput(): Valid command."""
        return_code, output = getstatusoutput('echo "Hello World"')
        self.assertEqual(0, return_code)
        self.assertEqual("Hello World", output)

    def test_getstatusoutput_return(self):
        """git_cache.command_execution.getstatusoutput(): Return code."""
        return_code, output = getstatusoutput('exit 12')
        self.assertEqual(12, return_code)
        self.assertEqual("", output)

        return_code, output = getstatusoutput('echo a; exit 12')
        self.assertEqual(12, return_code)
        self.assertEqual("a", output)

        return_code, output = getstatusoutput('cmd_doesnt_exist')
        self.assertNotEqual(0, return_code)
        self.assertEqual("", output)

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
