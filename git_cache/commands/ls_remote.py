# -*- coding: utf-8 -*-
"""
Handler for the git ls-remote command.

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
def git_ls_remote(all_args, global_options, command_args):
    """Handle a git ls-remote command.

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

    remote_url = None
    for arg in command_args:
        if arg.startswith('http://') or arg.startswith('https://') or arg.startswith('ssh://'):
            remote_url = arg
            break

    if remote_url is None:
        command = f"{command_with_options} remote get-url origin"
        retval, pull_url = getstatusoutput(command)
        if retval == 0 and pull_url.startswith(GITCACHE_DIR):
            command = f"{command_with_options} remote get-url --push origin"
            retval, push_url = getstatusoutput(command)
            if retval == 0:
                remote_url = push_url
            else:
                LOG.warning("Can't get push URL of the repository!")
        else:
            LOG.debug("Repository is not managed by gitcache!")

    if remote_url:
        database = Database()
        mirror = GitMirror(url=remote_url, database=database)
        mirror.update()
        database.increment_counter(mirror.path, "updates")
        config = mirror.config
        new_args = [x if x != remote_url else mirror.git_dir for x in all_args]
    else:
        new_args = all_args

    original_command_args = [real_git] + new_args
    return simple_call_command(original_command_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
