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
    # git lfs fetch [--recent|--all|--prune] [remote [ref...]]
    #  No Mirror Update: git lfs fetch (as it was already updated by other calls)
    #  No Mirror Update  git lfs fetch origin
    #  Mirror Update     git lfs fetch origin ref...
    #  Mirror Update:    git lfs fetch [--recent|--all|--prune] ...
    options = []
    remote = None
    refs = []
    ignore_next_arg = False
    for arg in command_args:
        if ignore_next_arg:
            ignore_next_arg = False
        elif arg in ['-I', '--include', '-X', '--exclude']:
            ignore_next_arg = True
        elif arg in ['--recent', '--all', '--prune']:
            options.append(arg)
        elif arg.startswith('-'):
            pass
        elif remote is None:
            remote = arg
        else:
            refs.append(arg)

    if options or refs:
        config = Config()

        global_options_str = ' '.join(["'%s'" % i for i in global_options])
        command_with_options = "%s %s" % (config.get("System", "RealGit"),
                                          global_options_str)

        if not refs:
            command = "%s rev-parse --abbrev-ref HEAD" % command_with_options
            retval, ref = getstatusoutput(command)
            if retval == 0:
                refs.append(ref)

        command = "%s remote get-url origin" % command_with_options
        retval, pull_url = getstatusoutput(command)
        if retval == 0 and pull_url.startswith(GITCACHE_DIR):
            command = "%s remote get-url --push origin" % command_with_options
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

    original_command_args = [config.get("System", "RealGit")] + all_args
    return simple_call_command(original_command_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
