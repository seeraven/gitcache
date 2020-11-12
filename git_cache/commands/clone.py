# -*- coding: utf-8 -*-
"""
Handler for the git clone command.

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
import logging

from ..command_execution import simple_call_command
from ..config import Config
from ..git_mirror import GitMirror


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def get_ref_from_args(args):
    """Extract the ref from the given git clone command arguments.

    Args:
        args (list): The arguments for the clone command.

    Return:
        Returns the reference specified by the -b/--branch option or
        None if none was found.
    """
    ref_is_next_arg = False

    for arg in args:
        if ref_is_next_arg:
            return arg
        if arg in ['-b', '--branch']:
            ref_is_next_arg = True
        elif arg.startswith('-b'):
            return arg[2:]
        elif arg.startswith('--branch='):
            return arg[9:]
    return None


def git_clone(all_args, command_args):
    """Handle a git clone command.

    Args:
        all_args (list):     All arguments to the 'git' command.
        command_args (list): The arguments for the clone command.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    remote_url = None
    for arg in command_args:
        if arg.startswith('http://') or arg.startswith('https://') or arg.startswith('ssh://'):
            remote_url = arg
            break

    if remote_url:
        mirror = GitMirror(url=remote_url)
        return mirror.clone_from_mirror(all_args, get_ref_from_args(command_args))

    LOG.debug("No remote URL found. Falling back to orginal git command.")
    config = Config()
    return simple_call_command([config.get("System", "RealGit")] + all_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
