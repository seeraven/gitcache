# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the git_cache.invocation_log module."""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from git_cache import invocation_log


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class InvocationLogTest(unittest.TestCase):
    """Test the invocation log helpers."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self._detail_log = os.path.join(self._tmpdir.name, "detail.log")
        self._summary_log = os.path.join(self._tmpdir.name, "summary.log")
        self._env_patch = mock.patch.multiple(
            invocation_log,
            GITCACHE_DETAIL_LOG=self._detail_log,
            GITCACHE_SUMMARY_LOG=self._summary_log,
            GITCACHE_DETAIL_LOG_LEVEL="DEBUG",
        )
        self._env_patch.start()
        invocation_log._write_error_reported = False  # pylint: disable=protected-access

    def tearDown(self):
        self._env_patch.stop()
        self._tmpdir.cleanup()

    def _read_file(self, path: str) -> str:
        with open(path, encoding="utf-8") as log_file:
            return log_file.read()

    def test_format_command_line_masks_credentials(self):
        """git_cache.invocation_log: Mask credentials in command lines."""
        command = invocation_log.format_command_line(["git", "clone", "https://user:secret@github.com/org/repo.git"])
        self.assertIn("[MASKED]", command)
        self.assertNotIn("secret", command)

    def test_format_command_line_normalizes_git_launcher_path(self):
        """git_cache.invocation_log: Normalize git launcher paths."""
        command = invocation_log.format_command_line(["/opt/gitcache/bin/git", "status", "-sb"])
        self.assertEqual(command, "git status -sb")

    def test_format_command_line_normalizes_gitcache_git_invocation(self):
        """git_cache.invocation_log: Normalize gitcache git invocations."""
        command = invocation_log.format_command_line(
            ["/usr/bin/python3", "/opt/gitcache", "git", "clone", "https://github.com/org/repo.git"]
        )
        self.assertEqual(command, "git clone https://github.com/org/repo.git")

    def test_log_subprocess_success_includes_exit_and_duration(self):
        """git_cache.invocation_log: Log successful subprocess metadata."""
        argv = ["git", "fetch", "origin"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("gitcache")
                invocation_log.log_subprocess(["git", "fetch", "origin"], 0, 42, "/build")
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        self.assertIn("---- SUBPROCESS ----", detail)
        self.assertIn("  cmd=git fetch origin", detail)
        self.assertIn("  cwd=/build", detail)
        self.assertIn("  exit=0  duration_ms=42", detail)

    def test_log_subprocess_masks_credentials(self):
        """git_cache.invocation_log: Mask credentials in subprocess logs."""
        argv = ["git", "clone", "https://user:secret@github.com/org/repo.git"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("gitcache")
                invocation_log.log_subprocess(
                    ["git", "clone", "https://user:secret@github.com/org/repo.git"],
                    0,
                    10,
                )
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        self.assertIn("[MASKED]", detail)
        self.assertNotIn("secret", detail)

    def test_mirrored_info_lines_use_info_prefix(self):
        """git_cache.invocation_log: Prefix mirrored log lines with [info]."""
        argv = ["git", "clone", "https://github.com/org/repo.git"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("gitcache")
                logging.getLogger("git_cache").setLevel(logging.DEBUG)
                logging.getLogger("git_cache.git_mirror").info("Repository seems not to use LFS. Skipping LFS fetch.")
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        self.assertIn("[info] Repository seems not to use LFS. Skipping LFS fetch.", detail)

    def test_gitcache_invocation_writes_summary_and_detail(self):
        """git_cache.invocation_log: Write summary and detail for gitcache calls."""
        argv = ["gitcache", "git", "clone", "https://github.com/org/repo.git"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                self.assertIsNotNone(context)
                context.set_mode("gitcache")
                context.record_cache("miss_create", "/home/user/.gitcache/org/repo.git")
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        summary = self._read_file(self._summary_log)

        self.assertIn("======== INVOCATION", detail)
        self.assertRegex(detail, r"======== INVOCATION[^\n]+\nts=[0-9]{4}-")
        self.assertIn("mode=gitcache", detail)
        self.assertIn("cache=miss_create", detail)
        self.assertIn("-------- SUMMARY --------", detail)
        self.assertIn("======== END INVOCATION", detail)
        self.assertIn("mode=gitcache cache=miss_create", summary)
        self.assertIn("exit=0", summary)
        self.assertIn("mirror=/home/user/.gitcache/org/repo.git", summary)
        self.assertNotIn(" pid=", f" {summary} ")

    def test_summary_omits_pid(self):
        """git_cache.invocation_log: Omit pid from summary lines."""
        argv = ["git", "status"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("realgit")
                context.set_exit_code(0)

        summary = self._read_file(self._summary_log)
        self.assertNotIn("pid=", summary)

    def test_routing_mode_transition(self):
        """git_cache.invocation_log: Record routing mode transitions."""
        argv = ["git", "clone", "https://github.com/org/repo.git"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("gitcache", "clone")
                context.set_mode("realgit", "url_pattern")
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        summary = self._read_file(self._summary_log)
        self.assertIn("[routing] mode=gitcache reason=clone", detail)
        self.assertIn("[routing] mode=realgit reason=url_pattern", detail)
        self.assertNotIn("->", detail)
        self.assertNotIn("reason=", summary)

    def test_mirror_masks_credentials_in_log_lines(self):
        """git_cache.invocation_log: Mask credentials in mirrored log lines."""
        argv = ["git", "clone", "https://user:secret@github.com/org/repo.git"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("gitcache")
                logging.getLogger("git_cache").setLevel(logging.DEBUG)
                logging.getLogger("git_cache.git_mirror").info(
                    "Execute command '/usr/bin/git clone https://user:secret@github.com/org/repo.git'"
                )
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        self.assertIn("[info]", detail)
        self.assertIn("[MASKED]", detail)
        self.assertNotIn("secret", detail)

    def test_command_execution_logs_not_mirrored_at_debug(self):
        """git_cache.invocation_log: Skip mirroring command_execution debug logs."""
        argv = ["git", "fetch"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("gitcache")
                logging.getLogger("git_cache").setLevel(logging.DEBUG)
                logging.getLogger("git_cache.command_execution_unix").debug(
                    "Execute command '/usr/bin/git fetch' (shell=False, cwd=None)"
                )
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        self.assertNotIn("Execute command '/usr/bin/git fetch'", detail)

    def test_detail_log_separates_invocations_with_blank_line(self):
        """git_cache.invocation_log: Separate invocations with a blank line."""
        argv = ["git", "status"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("realgit")
                context.set_exit_code(0)
            with invocation_log.invocation_context() as context:
                context.set_mode("realgit")
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        self.assertIn("======== END INVOCATION", detail)
        self.assertIn(
            "======== END INVOCATION (pid=",
            detail.split("======== INVOCATION git status")[1],
        )
        self.assertRegex(detail, r"======== END INVOCATION[^\n]*\n\n======== INVOCATION")

    def test_disabled_mode_minimal_detail(self):
        """git_cache.invocation_log: Write minimal detail output in disabled mode."""
        argv = ["git", "fetch", "origin"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("disabled")
                invocation_log.log_subprocess(["git", "fetch", "origin"], 0, 10, "/build")
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        summary = self._read_file(self._summary_log)

        self.assertIn("[routing] mode=disabled", detail)
        self.assertIn("---- SUBPROCESS ----", detail)
        self.assertIn("  cmd=git fetch origin", detail)
        self.assertIn("mode=disabled", summary)

    def test_admin_mode_does_not_mirror_internal_logs(self):
        """git_cache.invocation_log: Skip mirroring internal logs in admin mode."""
        argv = ["gitcache", "--show-statistics"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("admin")
                logging.getLogger("git_cache.git_cache_command").info("Statistics cleared.")
                context.set_exit_code(0)

        detail = self._read_file(self._detail_log)
        self.assertIn("[routing] mode=admin", detail)
        self.assertNotIn("Statistics cleared.", detail)

    def test_subprocess_failure_includes_stderr(self):
        """git_cache.invocation_log: Include stderr for failed subprocesses."""
        argv = ["git", "push"]
        with mock.patch.object(sys, "argv", argv):
            with invocation_log.invocation_context() as context:
                context.set_mode("realgit", "unhandled_command")
                invocation_log.log_subprocess(
                    ["git", "push"],
                    128,
                    50,
                    "/build",
                    b"",
                    b"fatal: permission denied\n",
                )
                context.set_exit_code(128)

        detail = self._read_file(self._detail_log)
        self.assertIn("  stderr:", detail)
        self.assertIn("    fatal: permission denied", detail)
        self.assertIn("fail_reason=git_error", self._read_file(self._summary_log))

    def test_parallel_writes_produce_complete_blocks(self):
        """git_cache.invocation_log: Produce complete blocks under parallel writes."""
        src = os.path.join(os.path.dirname(__file__), "..", "..", "src")
        script = f"""
import os, sys
sys.path.insert(0, {src!r})
os.environ['GITCACHE_DETAIL_LOG'] = {self._detail_log!r}
os.environ['GITCACHE_SUMMARY_LOG'] = {self._summary_log!r}
import git_cache.invocation_log as il
with il.invocation_context() as ctx:
    ctx.set_mode('realgit', 'unhandled_command')
    ctx.set_exit_code(0)
"""

        for _ in range(3):
            with subprocess.Popen([sys.executable, "-c", script]) as process:
                self.assertEqual(process.wait(), 0)

        detail = self._read_file(self._detail_log)
        self.assertEqual(detail.count("======== INVOCATION"), 3)
        self.assertEqual(detail.count("======== END INVOCATION"), 3)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
