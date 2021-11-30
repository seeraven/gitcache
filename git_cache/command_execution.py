# -*- coding: utf-8 -*-
"""
Module for command execution functions.

Copyright:
    2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>

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
import shutil
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
# pylint: disable=too-many-locals,too-many-statements
def call_command(command, command_timeout=None, output_timeout=None):
    """Call the given command with optional timeouts.

    This function calls the given command in a shell environment and applies a
    timeout on the whole command as well as a timeout on the stdout/stderr
    streams.

    The function returns the tuple (return code, stdout, stderr) with stdout
    and stderr as the byte buffers. To convert them to strings, use the
    'decode(encoding="utf-8", errors="ignore")' function.
    The return code will be -1000 for a command timeout and -2000 for
    a stdout timeout.

    Args:
        command (str):           The command to execute.
        command_timeout (float): The timeout of the whole command execution in seconds.
        output_timeout (float):  The timeout of stdout/stderr outputs.

    Returns:
        The tuple (return_code, stdout_buffer, stderr_buffer) with the return code
        of the command (or -1000 on a command timeout resp. -2000 on a stdout timeout)
        and the stdout/stderr buffers as byte arrays.
    """
    LOG.debug("Execute command '%s' in shell environment with command timeout of %s seconds and "
              "output timeout of %s seconds.", command, command_timeout, output_timeout)

    stdout_r, stdout_w = pty.openpty()
    stderr_r, stderr_w = pty.openpty()

    proc = subprocess.Popen(command,
                            bufsize=0,
                            shell=True,
                            stdout=stdout_w,
                            stderr=stderr_w)
    os.close(stdout_w)
    os.close(stderr_w)

    output_start_time = time.time()
    command_start_time = output_start_time
    command_timeout_occured = False
    output_timeout_occured = False
    buffer_size = 1024
    stdout_buffer = b''
    stderr_buffer = b''

    def read_buffer(read_fd, output_stream):
        buffer = b''
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
                LOG.debug("No stdout/stderr output received within %d seconds!",
                          (time.time() - output_start_time))
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
    sys.stderr.buffer.flush()

    return_code = proc.returncode
    if command_timeout_occured:
        return_code = -1000
    elif output_timeout_occured:
        return_code = -2000

    LOG.debug("Command '%s' finished with return code %d.", command, return_code)
    return (return_code, stdout_buffer, stderr_buffer)


# pylint: disable=too-many-arguments
def call_command_retry(command, num_retries, command_timeout=None, output_timeout=None,
                       remove_dir=None, abort_on_pattern=None):
    """Call the given command with automatic retries on error.

    The given command is called using the call_command() function and executed
    again as long as the return code of the command is not zero.

    Args:
        command (str):           The command to execute.
        num_retries (int):       Maximum number of retries of the call.
        command_timeout (float): The timeout of the whole command execution in seconds.
        output_timeout (float):  The timeout of stdout/stderr outputs.
        remove_dir (str):        If given, remove the directory on error.
        abort_on_pattern (str):  If given, the given pattern is search in stdout and
                                 stderr of a failed call. If found, this call returns
                                 with the return code -3000.

    Returns:
        The tuple (return_code, stdout_buffer, stderr_buffer) with the return code
        of the last execution of the command (or -1000 on a command timeout,
        -2000 on a stdout timeout or -3000 if the abort pattern was found) and the
        stdout/stderr buffers as byte arrays.
    """
    LOG.debug("Retry to execute command '%s' up to %d times.", command, num_retries)
    for retry in range(num_retries + 1):
        return_code, stdout_buffer, stderr_buffer = call_command(command, command_timeout,
                                                                 output_timeout)
        if return_code == 0:
            break

        if remove_dir:
            LOG.debug("Delete directory %s.", remove_dir)
            shutil.rmtree(remove_dir, ignore_errors=True)

        if abort_on_pattern:
            if (abort_on_pattern in stdout_buffer) or (abort_on_pattern in stderr_buffer):
                LOG.debug("Abort pattern '%s' found in stdout/stderr.", abort_on_pattern)
                return -3000, stdout_buffer, stderr_buffer
            LOG.debug("Abort pattern '%s' not found in stdout/stderr.", abort_on_pattern)

        if retry != num_retries:
            LOG.warning("Command '%s' failed. Starting retry %d of %d.",
                        command, retry + 1, num_retries)

    return return_code, stdout_buffer, stderr_buffer


def pretty_call_command_retry(action, pattern_cause, command, num_retries, **kwargs):
    """Call the given command with automatic retries on errors with a pretty output.

    This function wraps the call_command_retry() function and adds a suitable output
    for most calls.

    Args:
        action (str):        The action string. It should fit into the messages
                             like 'action timed out' or
                             'action was successfully completed'.
        pattern_cause (str): The cause when the abort_on_pattern key is used.
        command (str):       The command to execute.
        num_retries (int):   Maximum number of retries of the call.
        kwargs:              The arguments to call_command_retry().

    Returns:
        The tuple (return_code, stdout_buffer, stderr_buffer) with the return code
        of the last execution of the command (or -1000 on a command timeout,
        -2000 on a stdout timeout or -3000 if the abort pattern was found) and the
        stdout/stderr buffers as byte arrays.
    """
    LOG.info("Starting %s.", action)
    start_time = time.time()
    return_code, stdout_buffer, stderr_buffer = call_command_retry(command, num_retries, **kwargs)
    run_time = time.time() - start_time

    if return_code == 0:
        LOG.info("%s was successfully completed within %.1f seconds.", action, run_time)
    elif return_code == -1000:
        LOG.error("%s timed out after %.1f seconds!", action, run_time)
    elif return_code == -2000:
        LOG.error("%s stalled after %.1f seconds!", action, run_time)
    elif return_code == -3000:
        LOG.error("%s failed due to %s after %.1f seconds!", action, pattern_cause, run_time)
    else:
        LOG.error("%s failed after %.1f seconds with return code %d!",
                  action, run_time, return_code)

    return return_code, stdout_buffer, stderr_buffer


def simple_call_command(args):
    """Execute the command directly using a list of arguments.

    Args:
        args (list): List of arguments.

    Return:
        Returns the return code of the command.
    """
    command = ' '.join([f"'{i}'" for i in args])
    ret_code = os.WEXITSTATUS(os.system(command))
    return ret_code


def getstatusoutput(cmd):
    """Call the given command like the good old commands.getstatusoutput.

    Args:
        cmd (str): The command to execute.

    Return:
        Returns the tuple (return_code, output).
    """
    ret_val = 0
    cmd_output = None
    try:
        cmd_output = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as exception:
        cmd_output = b''
        if exception.output:
            cmd_output += exception.output
        if exception.stderr:
            cmd_output += exception.stderr
        ret_val = exception.returncode

    return (ret_val, cmd_output.decode(encoding="utf-8", errors="ignore").strip())


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
