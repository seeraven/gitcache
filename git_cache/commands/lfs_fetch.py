# -*- coding: utf-8 -*-
"""
Handler for the git lfs fetch command.

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
def git_lfs_fetch(all_args, global_options, command_args):
    """Handle a git lfs fetch command.

    Args:
        all_args (list):       All arguments to the 'git' command.
        global_options (list): The options given to git, not the command.
        command_args (list):   The arguments for the clone command.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    # git lfs fetch [options] [remote [ref...]]
    #  No Mirror Update: git lfs fetch (as it was already updated by other calls)
    #  No Mirror Update: git lfs fetch origin
    #  No Mirror Update: git lfs fetch <other origin>
    #  Mirror Update:    git lfs fetch <options> ... (as the options might include
    #                                                 not-fetched elements)
    #  Mirror Update     git lfs fetch origin ref...
    options_with_arg = ['-I', '--include', '-X', '--exclude']
    options = []
    remote = None
    refs = []
    add_next_arg = False
    for arg in command_args:
        if add_next_arg:
            options.append(arg)
            add_next_arg = False
        elif arg in options_with_arg:
            options.append(arg)
            add_next_arg = True
        elif arg.startswith('-'):
            options.append(arg)
        elif remote is None:
            remote = arg
        else:
            refs.append(arg)

    if remote is None:
        remote = 'origin'

    config = Config()
    real_git = config.get("System", "RealGit")
    if remote == 'origin':
        if options or refs:
            global_options_str = ' '.join([f"'{i}'" for i in global_options])
            command_with_options = f"{real_git} {global_options_str}"

            if not refs:
                command = f"{command_with_options} rev-parse --abbrev-ref HEAD"
                retval, ref = getstatusoutput(command)
                if retval == 0:
                    refs.append(ref)

            command = f"{command_with_options} remote get-url origin"
            retval, pull_url = getstatusoutput(command)
            if retval == 0 and pull_url.startswith(GITCACHE_DIR):
                command = f"{command_with_options} remote get-url --push origin"
                retval, push_url = getstatusoutput(command)
                if retval == 0:
                    database = Database()
                    mirror = GitMirror(url=push_url, database=database)
                    for ref in refs:
                        mirror.fetch_lfs(ref, options)
                else:
                    LOG.warning("Can't get push URL of the repository!")
            else:
                LOG.debug("Repository is not managed by gitcache!")

    original_command_args = [real_git] + all_args
    return simple_call_command(original_command_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
