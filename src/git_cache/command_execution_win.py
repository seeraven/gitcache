# -*- coding: utf-8 -*-
"""
Module for command execution function call_command() on Windows.

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
import logging
import subprocess
import sys
import time
from queue import Empty, Queue
from threading import Thread

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Exported Functions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals,too-many-statements,too-many-arguments,too-many-positional-arguments
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
    LOG.debug(
        "Execute command '%s' (shell=%s, cwd=%s) with command timeout of %s seconds and "
        "output timeout of %s seconds. stderr_capture=%s",
        command,
        shell,
        cwd,
        command_timeout,
        output_timeout,
        stderr_capture,
    )

    return_code = -1
    stdout_buffer = b""
    stderr_buffer = b""

    stdout_queue = Queue()
    stderr_queue = Queue()

    def enqueue_output(proc, stream, queue):
        """Read data from the stream and put it into the queue."""
        while proc.poll() is None:
            buffer = b""
            try:
                buffer = stream.read(buffer_size)
                # pylint: disable=bare-except
            except:  # noqa
                pass

            if buffer:
                queue.put(buffer)

    def dequeue_output(queue):
        """Read all pending data from the queue and return it."""
        output = b""
        finished = False
        while not finished:
            try:
                buffer = queue.get_nowait()
                output += buffer
            except Empty:
                finished = True
        return output

    def fill_buffers():
        """Handle stdout/stderr outputs."""
        nonlocal stdout_buffer, stderr_buffer

        stdout_output = dequeue_output(stdout_queue)
        stderr_output = dequeue_output(stderr_queue)

        if stdout_output:
            stdout_buffer += stdout_output
            sys.stdout.buffer.write(stdout_output)
            sys.stdout.buffer.flush()

        if stderr_output:
            stderr_buffer += stderr_output
            sys.stderr.buffer.write(stderr_output)
            sys.stderr.buffer.flush()

        return bool(stdout_output or stderr_output)

    def kill(proc):
        subprocess.call(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    try:
        with subprocess.Popen(
            command,
            bufsize=0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE if stderr_capture else None,
            cwd=cwd,
            shell=shell,
        ) as proc:
            output_start_time = time.time()
            command_start_time = output_start_time
            command_timeout_occured = False
            output_timeout_occured = False
            buffer_size = 1024

            stdout_thread = Thread(target=enqueue_output, args=(proc, proc.stdout, stdout_queue))
            stdout_thread.start()
            if stderr_capture:
                stderr_thread = Thread(target=enqueue_output, args=(proc, proc.stderr, stderr_queue))
                stderr_thread.start()

            while proc.poll() is None:
                if fill_buffers():
                    output_start_time = time.time()

                elif proc.poll() is None:
                    if output_timeout and ((time.time() - output_start_time) >= output_timeout):
                        LOG.warning(
                            "No stdout/stderr output received within %d seconds!", (time.time() - output_start_time)
                        )
                        output_timeout_occured = True
                        kill(proc)
                        break

                    if command_timeout and ((time.time() - command_start_time) >= command_timeout):
                        LOG.warning("Timeout occured after %d seconds!", (time.time() - command_start_time))
                        command_timeout_occured = True
                        kill(proc)
                        break

                    time.sleep(0.25)

            # To cleanup any pending resources
            stdout_thread.join()
            if stderr_capture:
                stderr_thread.join()
            fill_buffers()
            proc.wait()

            sys.stdout.buffer.flush()
            if stderr_capture:
                sys.stderr.buffer.flush()

            return_code = proc.returncode
            if command_timeout_occured:
                return_code = -1000
            elif output_timeout_occured:
                return_code = -2000

            LOG.debug("Command '%s' finished with return code %d.", command, return_code)
    except FileNotFoundError:
        return_code = 127

    return (return_code, stdout_buffer, stderr_buffer)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
