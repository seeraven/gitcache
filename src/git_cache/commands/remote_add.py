"""
Handler for the git remote add origin command.

Copyright:
    2025 by Clemens Rabe <clemens.rabe@clemensrabe.de>

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
from ..database import Database
from ..git_mirror import GitMirror
from ..git_options import GitOptions
from .helpers import get_pull_url, use_mirror_for_remote_url

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals,too-many-statements
def git_remote_add(git_options: GitOptions) -> int:
    """Handle a git remote add command.

    Args:
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    # Handle only a "git remote add origin"
    if len(git_options.command_args) >= 2 and git_options.command_args[0] == "origin":
        # Do not handle when the "--mirror" option is used
        if not any(option.startswith("--mirror") for option in git_options.command_options):
            remote_url = git_options.command_args[1]
            if get_pull_url(git_options) is None:
                if use_mirror_for_remote_url(remote_url):
                    database = Database()
                    mirror = GitMirror(url=remote_url, database=database)
                    mirror.ensure_exists()
                    return mirror.configure_git_for_mirror(git_options)

                LOG.debug("Ignoring 'git remote add' command as the remote url is excluded in the configuration.")
            else:
                LOG.debug("Ignoring 'git remote add' command as there is already a remote set up.")
        else:
            LOG.debug("Ignoring 'git remote add' command as the '--mirror' option was used.")

    LOG.debug("Ignoring 'git remote add' command with additional arguments %s.", git_options.command_args)

    # Fallback to original git
    return simple_call_command(git_options.get_real_git_all_args())
