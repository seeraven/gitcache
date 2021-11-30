# -*- coding: utf-8 -*-
"""
Handler for the git checkout command.

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
from ..config import Config
from ..database import Database
from ..git_mirror import GitMirror
from ..global_settings import GITCACHE_DIR


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals
def git_checkout(all_args, global_options, command_args):
    """Handle a git checkout command.

    Args:
        all_args (list):       All arguments to the 'git' command.
        global_options (list): The options given to git, not the command.
        command_args (list):   The arguments for the clone command.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    config = Config()

    global_options_str = ' '.join([f"'{i}'" for i in global_options])
    real_git = config.get("System", "RealGit")
    command_with_options = f"{real_git} {global_options_str}"

    # Collect all refs for an lfs fetch
    ref_candidates = [x for x in command_args if not x.startswith('-') and not x.startswith(':')]
    lfs_fetch_refs = []
    for ref in ref_candidates:
        command = f"{command_with_options} show-ref -q {ref}"
        retval, _ = getstatusoutput(command)
        if retval == 0:
            lfs_fetch_refs.append(ref)

    if lfs_fetch_refs:
        command = f"{command_with_options} remote get-url origin"
        retval, pull_url = getstatusoutput(command)
        if retval == 0 and pull_url.startswith(GITCACHE_DIR):
            command = f"{command_with_options} remote get-url --push origin"
            retval, push_url = getstatusoutput(command)
            if retval == 0:
                database = Database()
                mirror = GitMirror(url=push_url, database=database)
                for ref in lfs_fetch_refs:
                    mirror.fetch_lfs(ref)
            else:
                LOG.warning("Can't get push URL of the repository!")
        else:
            LOG.debug("Repository is not managed by gitcache!")

    original_command_args = [real_git] + all_args
    return simple_call_command(original_command_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
