# -*- coding: utf-8 -*-
"""
Handler for the git submodule init command.

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

from ..command_execution import getstatusoutput, simple_call_command
from ..git_options import GitOptions
from .helpers import get_mirror_url, get_pull_url

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def git_submodule_init(git_options: GitOptions) -> int:
    """Handle a git submodule init command.

    The 'submodule init' command initializes the git configuration for the
    submodules. To support relative paths, we restore the original URL of a
    mirror before calling the 'submodule init' command and restore it
    afterwards.

    Args:
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    mirror_url = get_mirror_url(git_options)
    if mirror_url:
        pull_url = get_pull_url(git_options)

        command = git_options.get_real_git_with_options()
        command += ["remote", "set-url", "origin", mirror_url]
        retval, _ = getstatusoutput(command)
        if retval == 0:
            retval = simple_call_command(git_options.get_real_git_all_args())
        else:
            LOG.warning("Can't restore original pull URL of the repository!")

        command = git_options.get_real_git_with_options()
        command += ["remote", "set-url", "origin", pull_url]
        _, _ = getstatusoutput(command)

        command = git_options.get_real_git_with_options()
        command += ["remote", "set-url", "--push", "origin", mirror_url]
        _, _ = getstatusoutput(command)
        return retval

    # Fallback to original git
    return simple_call_command(git_options.get_real_git_all_args())


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
