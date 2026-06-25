# -*- coding: utf-8 -*-
"""
Invocation logging to detail and summary log files.

Copyright:
    2026 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging
import os
import re
import shlex
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional

import portalocker

from .global_settings import GITCACHE_DETAIL_LOG, GITCACHE_DETAIL_LOG_LEVEL, GITCACHE_SUMMARY_LOG
from .helpers import strip_credentials

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
_HEADER_COMMAND_MAX_LEN = 200
_STREAM_MAX_BYTES = 64 * 1024
_CACHE_PRIORITY = {
    "lock_timeout": 4,
    "miss_create": 3,
    "hit_update": 2,
    "hit_skip": 1,
}
_SKIP_MIRROR_LOGGER_PREFIXES = ("git_cache.command_execution",)
_DETAIL_INDENT = "  "

# -----------------------------------------------------------------------------
# Module State
# -----------------------------------------------------------------------------
# pylint: disable=invalid-name
_current_context: Optional["InvocationContext"] = None
_write_error_reported = False
# pylint: enable=invalid-name


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _utc_timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def _is_logging_enabled() -> bool:
    return bool(GITCACHE_DETAIL_LOG or GITCACHE_SUMMARY_LOG)


def is_detail_log_enabled() -> bool:
    """Return whether the detail log file is configured."""
    return bool(GITCACHE_DETAIL_LOG)


def _ensure_log_dir(path: str) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    if directory:
        os.makedirs(directory, exist_ok=True)


def _write_block(path: Optional[str], text: str) -> None:
    global _write_error_reported  # pylint: disable=global-statement

    if not path:
        return

    if not text.endswith("\n"):
        text += "\n"

    try:
        _ensure_log_dir(path)
        with portalocker.Lock(path, "a", timeout=60) as log_file:
            log_file.write(text)
            log_file.flush()
            fchmod = getattr(os, "fchmod", None)
            if fchmod is not None:
                try:
                    fchmod(log_file.fileno(), 0o600)
                except OSError:
                    pass
    except OSError as error:
        if not _write_error_reported:
            _write_error_reported = True
            print(f"gitcache: failed to write log file '{path}': {error}", file=sys.stderr)


def _mask_argument(argument: str) -> str:
    if "://" in argument or argument.startswith("git@"):
        return strip_credentials(argument, mask=True)
    return argument


def _mask_log_message(message: str) -> str:
    if "://" not in message and "git@" not in message:
        return message

    parts = re.split(r"(\S+://\S+|git@\S+)", message)
    return "".join(
        strip_credentials(part, mask=True) if ("://" in part or part.startswith("git@")) else part for part in parts
    )


def _should_mirror_log_record(record: logging.LogRecord) -> bool:
    """Return whether a git_cache log record should be copied into the detail log.

    Subprocess output is already recorded via log_subprocess() (---- SUBPROCESS ----
    blocks) from command_execution.py. Loggers listed in _SKIP_MIRROR_LOGGER_PREFIXES
    are excluded so those records are not duplicated as [info] mirror lines.
    """
    return not any(record.name.startswith(prefix) for prefix in _SKIP_MIRROR_LOGGER_PREFIXES)


def _basename_is_git(name: str) -> bool:
    return os.path.basename(name) in ("git", "git.exe")


def normalize_invocation_argv(argv: List[str]) -> List[str]:
    """Return argv with a readable program name for log output."""
    if not argv:
        return argv

    if _basename_is_git(argv[0]) or os.path.basename(argv[0]) == "gitcache":
        return [os.path.basename(argv[0])] + argv[1:]

    if len(argv) >= 3 and os.path.basename(argv[1]) == "gitcache" and _basename_is_git(argv[2]):
        return [os.path.basename(argv[2])] + argv[3:]

    if len(argv) >= 2 and os.path.basename(argv[1]) == "gitcache":
        return ["gitcache"] + argv[2:]

    return argv


def mask_argv(argv: List[str]) -> List[str]:
    """Return argv with credentials masked in URL-like arguments."""
    return [_mask_argument(argument) for argument in argv]


def format_command_line(argv: List[str]) -> str:
    """Format argv as a shell-like command string with masking."""
    return " ".join(shlex.quote(_mask_argument(argument)) for argument in normalize_invocation_argv(argv))


def _decode_stream(buffer: bytes) -> str:
    if not buffer:
        return ""
    text = buffer.decode(encoding="utf-8", errors="replace")
    if len(buffer) > _STREAM_MAX_BYTES:
        return text[:_STREAM_MAX_BYTES] + "\n... [truncated]"
    return text


def _quote_summary_value(value: str) -> str:
    if not value:
        return '""'
    if re.search(r'[\s="]', value):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def _truncate_header_command(command: str) -> str:
    if len(command) <= _HEADER_COMMAND_MAX_LEN:
        return command
    return command[: _HEADER_COMMAND_MAX_LEN - 1] + "…"


def _indent_subprocess_body(lines: List[str]) -> List[str]:
    """Indent subprocess detail lines; the marker line stays at column 0."""
    return [_DETAIL_INDENT + line for line in lines]


def get_context() -> Optional["InvocationContext"]:
    """Return the active invocation context, if any."""
    return _current_context


# -----------------------------------------------------------------------------
# Logging Handler
# -----------------------------------------------------------------------------
class InvocationDetailLogHandler(logging.Handler):
    """Mirror selected log records into the detail log file."""

    def __init__(self, context: "InvocationContext") -> None:
        super().__init__(level=getattr(logging, GITCACHE_DETAIL_LOG_LEVEL.upper(), logging.INFO))
        self._context = context

    def emit(self, record: logging.LogRecord) -> None:
        if not self._context.log_mirror_enabled:
            return
        if not record.name.startswith("git_cache"):
            return
        if not _should_mirror_log_record(record):
            return
        try:
            message = _mask_log_message(self.format(record))
            self._context.write_log_mirror_line(message)
        except Exception:  # pylint: disable=broad-except
            self.handleError(record)


# -----------------------------------------------------------------------------
# Invocation Context
# -----------------------------------------------------------------------------
# pylint: disable=too-many-instance-attributes
class InvocationContext:
    """Collect invocation metadata and write structured log output."""

    def __init__(self) -> None:
        self.pid = os.getpid()
        self.pwd = os.getcwd()
        self.argv = sys.argv[:]
        self.start_time = time.time()
        self.mode: Optional[str] = None
        self.reason: Optional[str] = None
        self.cache_events: List[str] = []
        self.mirror: Optional[str] = None
        self.exit_code = 0
        self.log_mirror_enabled = False
        self._log_handler: Optional[InvocationDetailLogHandler] = None
        self._detail_started = False

    def start(self) -> None:
        """Write the detail log header for this invocation."""
        if not _is_logging_enabled():
            return

        if GITCACHE_DETAIL_LOG:
            command = _truncate_header_command(format_command_line(self.argv))
            header = (
                f"======== INVOCATION {command} in {self.pwd} (pid={self.pid}) ========\n" f"ts={_utc_timestamp()}\n"
            )
            _write_block(GITCACHE_DETAIL_LOG, header)
            self._detail_started = True

    def set_exit_code(self, exit_code) -> None:
        """Store the process exit code for summary output."""
        if exit_code is None:
            self.exit_code = 0
        elif isinstance(exit_code, int):
            self.exit_code = exit_code
        else:
            self.exit_code = 1

    def set_mode(self, mode: str, reason: Optional[str] = None) -> None:
        """Record routing mode and optionally enable log mirroring."""
        previous_mode = self.mode
        self.mode = mode
        self.reason = reason
        if mode in ("disabled", "admin"):
            self.log_mirror_enabled = False
        elif mode in ("gitcache", "realgit"):
            self.log_mirror_enabled = True
            self._install_log_handler()

        if GITCACHE_DETAIL_LOG and self._detail_started and previous_mode != mode:
            line = f"[routing] mode={mode}"
            if reason:
                line += f" reason={reason}"
            _write_block(GITCACHE_DETAIL_LOG, line)

    def record_cache(self, event: str, mirror: Optional[str] = None) -> None:
        """Record a cache event for summary and detail output."""
        self.cache_events.append(event)
        if mirror:
            self.mirror = mirror
        if GITCACHE_DETAIL_LOG and self._detail_started:
            line = f"[cache] {event}"
            if mirror:
                line += f" mirror={mirror}"
            _write_block(GITCACHE_DETAIL_LOG, line)

    def write_log_mirror_line(self, line: str) -> None:
        """Append a mirrored log line to the detail log."""
        if GITCACHE_DETAIL_LOG and self._detail_started:
            _write_block(GITCACHE_DETAIL_LOG, f"[info] {line}")

    def _install_log_handler(self) -> None:
        if self._log_handler or not GITCACHE_DETAIL_LOG:
            return
        self._log_handler = InvocationDetailLogHandler(self)
        self._log_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger("git_cache").addHandler(self._log_handler)

    def _remove_log_handler(self) -> None:
        if not self._log_handler:
            return
        logging.getLogger("git_cache").removeHandler(self._log_handler)
        self._log_handler = None

    def _primary_cache_event(self) -> Optional[str]:
        if not self.cache_events:
            return None
        return max(self.cache_events, key=lambda event: _CACHE_PRIORITY.get(event, 0))

    def _fail_reason(self) -> Optional[str]:
        if self.exit_code == 0:
            return None
        if self.exit_code in (-1000, -2000):
            return "timeout"
        if "lock_timeout" in self.cache_events:
            return "lock"
        return "git_error"

    def _build_summary_line(self, duration_ms: int) -> str:
        mode = self.mode or "realgit"
        fields = [f"ts={_utc_timestamp()}", f"mode={mode}"]

        cache_event = self._primary_cache_event()
        if mode == "gitcache" and cache_event:
            fields.append(f"cache={cache_event}")

        fields.append(f"cmd={_quote_summary_value(format_command_line(self.argv))}")
        fields.append(f"pwd={self.pwd}")
        fields.append(f"exit={self.exit_code}")
        fields.append(f"duration_ms={duration_ms}")

        if mode == "gitcache" and self.mirror:
            fields.append(f"mirror={self.mirror}")

        fail_reason = self._fail_reason()
        if fail_reason:
            fields.append(f"fail_reason={fail_reason}")

        return " ".join(fields)

    def finalize(self) -> None:
        """Write summary output and tear down log handlers."""
        if not _is_logging_enabled():
            return

        duration_ms = int((time.time() - self.start_time) * 1000)
        summary_line = self._build_summary_line(duration_ms)

        if GITCACHE_SUMMARY_LOG:
            _write_block(GITCACHE_SUMMARY_LOG, summary_line)

        if GITCACHE_DETAIL_LOG and self._detail_started:
            _write_block(
                GITCACHE_DETAIL_LOG,
                f"-------- SUMMARY --------\n{summary_line}",
            )
            _write_block(
                GITCACHE_DETAIL_LOG,
                f"======== END INVOCATION (pid={self.pid}) exit={self.exit_code} duration_ms={duration_ms} ========",
            )
            _write_block(GITCACHE_DETAIL_LOG, "")

        self._remove_log_handler()


@contextmanager
def invocation_context():
    """Context manager for one gitcache process invocation."""
    global _current_context  # pylint: disable=global-statement

    if not _is_logging_enabled():
        yield None
        return

    context = InvocationContext()
    _current_context = context
    context.start()
    try:
        yield context
    finally:
        context.finalize()
        _current_context = None


def set_mode(mode: str, reason: Optional[str] = None) -> None:
    """Set routing mode on the active invocation context."""
    if _current_context:
        _current_context.set_mode(mode, reason)


def set_mode_disabled() -> None:
    """Mark the active invocation as disabled."""
    set_mode("disabled")


def set_mode_realgit(reason: Optional[str] = None) -> None:
    """Mark the active invocation as forwarded to real git."""
    set_mode("realgit", reason)


def set_mode_gitcache(reason: Optional[str] = None) -> None:
    """Mark the active invocation as handled by gitcache."""
    set_mode("gitcache", reason)


def set_mode_admin() -> None:
    """Mark the active invocation as an admin command."""
    set_mode("admin")


def record_cache(event: str, mirror: Optional[str] = None) -> None:
    """Record a cache event on the active invocation context."""
    if _current_context:
        _current_context.record_cache(event, mirror)


# pylint: disable=too-many-arguments,too-many-positional-arguments
def log_subprocess(
    command,
    exit_code: int,
    duration_ms: int,
    cwd: Optional[str] = None,
    stdout_buffer: bytes = b"",
    stderr_buffer: bytes = b"",
) -> None:
    """Write a subprocess execution block to the detail log."""
    context = _current_context
    if not GITCACHE_DETAIL_LOG or not context or not context._detail_started:  # pylint: disable=protected-access
        return

    if isinstance(command, str):
        command_str = command
    else:
        command_str = format_command_line(command)

    body = [
        f"cmd={command_str}",
        f"cwd={cwd or os.getcwd()}",
        f"exit={exit_code}  duration_ms={duration_ms}",
    ]

    if exit_code != 0:
        stdout_text = _decode_stream(stdout_buffer)
        stderr_text = _decode_stream(stderr_buffer)
        body.append("stdout:")
        body.extend(f"  {line}" if line else "  " for line in stdout_text.splitlines() or [""])
        body.append("stderr:")
        body.extend(f"  {line}" if line else "  " for line in stderr_text.splitlines() or [""])

    lines = ["---- SUBPROCESS ----", *_indent_subprocess_body(body)]
    _write_block(GITCACHE_DETAIL_LOG, "\n".join(lines))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
