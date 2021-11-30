# -*- coding: utf-8 -*-
"""
Handler for the git fetch command.

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
import os

from ..command_execution import getstatusoutput, pretty_call_command_retry
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
# pylint: disable=too-many-locals,too-many-statements
def git_fetch(all_args, global_options, command_args):
    """Handle a git fetch command.

    Args:
        all_args (list):       All arguments to the 'git' command.
        global_options (list): The options given to git, not the command.
        command_args (list):   The arguments for the fetch command.

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
        action = f"Fetch from mirror {mirror.path}"
        new_args = [x if x != remote_url else mirror.git_dir for x in all_args]

        # We configure the LFS storage here to support the Jenkins way
        # of cloning git repositories.
        LOG.info("Configuring LFS.")
        paths = []
        save_next_path = False
        for arg in global_options:
            if save_next_path:
                paths.append(arg)
                save_next_path = False
            elif arg == '-C':
                save_next_path = True
            elif arg == 'fetch':
                break

        command = ';'.join([f"cd {x}" for x in paths])
        if command != '':
            command += ';'
        command += f"{real_git} config --local lfs.url {mirror.url}/info/lfs"
        if config.get('LFS', 'PerMirrorStorage'):
            command += f";{real_git} config --local lfs.storage {mirror.git_lfs_dir}"
        os.system(command)
    else:
        action = "Fetch"
        new_args = all_args

    original_command_args = [real_git] + new_args

    return_code, _, _ = pretty_call_command_retry(
        action,
        '',
        ' '.join([f"'{i}'" for i in original_command_args]),
        num_retries=config.get("Update", "Retries"),
        command_timeout=config.get("Update", "CommandTimeout"),
        output_timeout=config.get("Update", "OutputTimeout"))

    return return_code


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
