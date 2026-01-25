# -*- coding: utf-8 -*-
"""
Module for command execution function call_command() on linux etc.

Copyright:
    2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import errno
import logging
import os
import pty
import select
import subprocess
import sys
import time

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Exported Functions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals,too-many-statements,too-many-arguments,too-many-positional-arguments,too-many-branches
def call_command(command, cwd=None, shell=False, command_timeout=None, output_timeout=None, stderr_capture=True):
    """Call the given command with optional timeouts.

    This function calls the given command and applies a timeout on the whole
    command as well as a timeout on the stdout/stderr streams.

    The function returns the tuple (return code, stdout, stderr) with stdout
    and stderr as the byte buffers. To convert them to strings, use the
    'decode(encoding="utf-8", errors="ignore")' function.
    The return code will be -1000 for a command timeout and -2000 for
    a stdout timeout.

    Args:
        command (list):          The command to execute as a list of command line
                                 arguments.
        cwd (str):               If given, the working directory. Otherwise the
                                 current working directory is used.
        shell (bool):            Should be set to False. If set to True, the command
                                 should be given as a string and is interpreted by
                                 a shell.
        command_timeout (float): The timeout of the whole command execution in seconds.
        output_timeout (float):  The timeout of stdout/stderr outputs.
        stderr_capture (bool):   Flag indicating stderr should be captured.

    Returns:
        The tuple (return_code, stdout_buffer, stderr_buffer) with the return code
        of the command (or -1000 on a command timeout resp. -2000 on a stdout timeout)
        and the stdout/stderr buffers as byte arrays.
    """
    if isinstance(command, str):
        command_str = command
    else:
        command_str = " ".join(command)

    LOG.debug(
        "Execute command '%s' (shell=%s, cwd=%s) with command timeout of %s seconds and "
        "output timeout of %s seconds. stderr_capture=%s",
        command_str,
        shell,
        cwd,
        command_timeout,
        output_timeout,
        stderr_capture,
    )

    stdout_r, stdout_w = pty.openpty()
    stderr_r, stderr_w = pty.openpty()

    return_code = -1
    stdout_buffer = b""
    stderr_buffer = b""
    try:
        with subprocess.Popen(
            command, bufsize=0, cwd=cwd, shell=shell, stdout=stdout_w, stderr=stderr_w if stderr_capture else None
        ) as proc:
            os.close(stdout_w)
            os.close(stderr_w)

            output_start_time = time.time()
            command_start_time = output_start_time
            command_timeout_occured = False
            output_timeout_occured = False
            buffer_size = 1024

            def read_buffer(read_fd, output_stream):
                buffer = b""
                try:
                    buffer = os.read(read_fd, buffer_size)
                except OSError as exception:
                    if exception.errno != errno.EIO:
                        raise
                else:
                    output_stream.buffer.write(buffer)
                    output_stream.buffer.flush()
                return buffer

            while proc.poll() is None:
                # Since the select call can't detect whether the process exited, we use a
                # small timeout on the select call (one second) and check afterwards for
                # a timeout on the stdout/stderr streams
                streams_ready = select.select([stdout_r, stderr_r], [], [], 1.0)[0]
                if streams_ready:
                    if stdout_r in streams_ready:
                        stdout_buffer += read_buffer(stdout_r, sys.stdout)
                    if stderr_r in streams_ready:
                        stderr_buffer += read_buffer(stderr_r, sys.stderr)
                    output_start_time = time.time()

                elif proc.poll() is None:
                    if output_timeout and ((time.time() - output_start_time) >= output_timeout):
                        LOG.debug(
                            "No stdout/stderr output received within %d seconds!", (time.time() - output_start_time)
                        )
                        output_timeout_occured = True
                        proc.kill()
                        break

                    if command_timeout and ((time.time() - command_start_time) >= command_timeout):
                        LOG.debug("Timeout occured after %d seconds!", (time.time() - command_start_time))
                        command_timeout_occured = True
                        proc.kill()
                        break

            # To cleanup any pending resources
            proc.wait()
            os.close(stdout_r)
            os.close(stderr_r)
            sys.stdout.buffer.flush()
            if stderr_capture:
                sys.stderr.buffer.flush()

            return_code = proc.returncode
            if command_timeout_occured:
                return_code = -1000
            elif output_timeout_occured:
                return_code = -2000

            LOG.debug("Command '%s' finished with return code %d.", command_str, return_code)
    except FileNotFoundError:
        return_code = 127

    return (return_code, stdout_buffer, stderr_buffer)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
