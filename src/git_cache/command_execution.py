# -*- coding: utf-8 -*-
"""
Module for command execution functions.

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
import platform
import subprocess
import time

from .helpers import rmtree

if platform.system().lower().startswith("win"):
    # pylint: disable=import-error
    from .command_execution_win import call_command
else:
    # pylint: disable=import-error
    from .command_execution_unix import call_command

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
ON_WINDOWS = platform.system().lower().startswith("win")
STDERR_DISABLE_PATTERNS = ["Permission denied (publickey).".encode()]


# -----------------------------------------------------------------------------
# Exported Functions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-arguments
def call_command_retry(
    command,
    num_retries,
    cwd=None,
    shell=False,
    command_timeout=None,
    output_timeout=None,
    remove_dir=None,
    abort_on_pattern=None,
):
    """Call the given command with automatic retries on error.

    The given command is called using the call_command() function and executed
    again as long as the return code of the command is not zero.

    Args:
        command (list):          The command to execute as a list of command line
                                 arguments.
        num_retries (int):       Maximum number of retries of the call.
        cwd (str):               If given, the working directory. Otherwise the
                                 current working directory is used.
        shell (bool):            Should be set to False. If set to True, the command
                                 should be given as a string and is interpreted by
                                 a shell.
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
    if isinstance(command, str):
        command_str = command
    else:
        command_str = " ".join(command)

    stderr_capture = True
    LOG.debug("Retry to execute command '%s' up to %d times.", command_str, num_retries)
    for retry in range(num_retries + 1):
        return_code, stdout_buffer, stderr_buffer = call_command(
            command,
            cwd=cwd,
            shell=shell,
            command_timeout=command_timeout,
            output_timeout=output_timeout,
            stderr_capture=stderr_capture,
        )
        if return_code == 0:
            break

        if ON_WINDOWS and stderr_capture:
            for pattern in STDERR_DISABLE_PATTERNS:
                if pattern in stderr_buffer:
                    LOG.info(
                        "Found pattern '%s' indicating we should disable stderr forwarding "
                        "as a workaround on Windows to enable git asking for a password.",
                        pattern,
                    )
                    stderr_capture = False
                    break

        if remove_dir:
            rmtree(remove_dir, ignore_errors=True)

        if abort_on_pattern:
            if (abort_on_pattern in stdout_buffer) or (abort_on_pattern in stderr_buffer):
                LOG.debug("Abort pattern '%s' found in stdout/stderr.", abort_on_pattern)
                return -3000, stdout_buffer, stderr_buffer
            LOG.debug("Abort pattern '%s' not found in stdout/stderr.", abort_on_pattern)

        if retry != num_retries:
            LOG.warning(
                "Command '%s' failed with return code %d. Starting retry %d of %d.",
                command_str,
                return_code,
                retry + 1,
                num_retries,
            )

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
        command (list):      The command to execute as a list of command line
                             arguments.
        num_retries (int):   Maximum number of retries of the call.
        kwargs:              The arguments to call_command_retry() besides
                             command and num_retries.

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
        LOG.error("%s failed after %.1f seconds with return code %d!", action, run_time, return_code)

    return return_code, stdout_buffer, stderr_buffer


def simple_call_command(cmd, shell=False, cwd=None):
    """Execute the command directly using a list of arguments.

    Args:
        cmd (list):   The command to execute as a list of arguments.
        shell (bool): If set to True the command is executed in a shell.
                      Only use this option if absolutely necessary!
        cwd (str):    The working directory. If not specified, the current
                      working directory is used.

    Return:
        Returns the return code of the command.
    """
    try:
        # pylint: disable=subprocess-run-check
        result = subprocess.run(cmd, shell=shell, cwd=cwd)
    except FileNotFoundError:
        return 127

    return result.returncode


def getstatusoutput(cmd, shell=False, cwd=None):
    """Call the given command like the good old commands.getstatusoutput.

    Executes the command and capture the stdout. The stderr is ignored by
    piping it to a null device.

    Args:
        cmd (list):   The command to execute as a list of arguments.
        shell (bool): If set to True the command is executed in a shell.
                      Only use this option if absolutely necessary!
        cwd (str):    The working directory. If not specified, the current
                      working directory is used.

    Return:
        Returns the tuple (return_code, output). If the command was not found
        the return code is 127 (with shell=True this might differ).
    """
    try:
        # pylint: disable=subprocess-run-check
        result = subprocess.run(cmd, shell=shell, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return (127, "")

    return (result.returncode, result.stdout.decode(encoding="utf-8", errors="ignore").strip())


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
