# -*- coding: utf-8 -*-
"""
Helpers for the git commands.

Copyright:
    2021 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging

from ..command_execution import getstatusoutput
from ..global_settings import GITCACHE_DIR


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def get_pull_url(git_options):
    """Get the pull url of the remote origin.

    Args:
        git_options (obj): The GitOptions object.

    Return:
        Returns the pull url or None on error.
    """
    command_with_options = git_options.get_real_git_with_options()
    command = f"{command_with_options} remote get-url origin"
    retval, pull_url = getstatusoutput(command)
    if retval == 0:
        return pull_url
    return None


def get_mirror_url(git_options):
    """Derive the mirror URL of a repository.

    Args:
        git_options (obj): The GitOptions object.

    Return:
        Returns the mirror url or None if the repository does not look like
        a mirror.
    """
    pull_url = get_pull_url(git_options)
    if pull_url and pull_url.startswith(GITCACHE_DIR):
        command_with_options = git_options.get_real_git_with_options()
        command = f"{command_with_options} remote get-url --push origin"
        retval, push_url = getstatusoutput(command)
        if retval == 0:
            return push_url
        LOG.warning("Can't get push URL of the repository!")
    else:
        LOG.debug("Repository is not managed by gitcache!")

    return None


def get_current_ref(git_options):
    """Get the current ref of a repository.

    Args:
        git_options (obj): The GitOptions object.

    Return:
        Returns the current ref.
    """
    command_with_options = git_options.get_real_git_with_options()
    command = f"{command_with_options} rev-parse --abbrev-ref HEAD"
    retval, ref = getstatusoutput(command)
    if retval == 0:
        return ref
    return None


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
