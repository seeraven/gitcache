# -*- coding: utf-8 -*-
"""
Handler for the git submodule update command.

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

from ..command_execution import getstatusoutput, simple_call_command
from ..config import Config
from ..global_settings import GITCACHE_DIR


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals,too-many-statements
def git_submodule_update(called_as, all_args, global_options, command_args):
    """Handle a git submodule update command.

    Args:
        called_as (list):      The arguments used for the command call.
        all_args (list):       All arguments to the 'git' command.
        global_options (list): The options given to git, not the command.
        command_args (list):   The options given to the git subcommand.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    config = Config()

    called_as_str = ' '.join(called_as)
    global_options_str = ' '.join([f"'{i}'" for i in global_options])
    real_git = config.get("System", "RealGit")
    command_with_options = f"{real_git} {global_options_str}"

    # Translate all '-C' options into a list of 'cd' commands
    paths = []
    save_next_path = False
    for arg in global_options:
        if save_next_path:
            paths.append(arg)
            save_next_path = False
        elif arg == '-C':
            save_next_path = True

    # Capture '--init' option and extract all paths to update (may be empty)
    has_init = '--init' in command_args
    update_paths = []
    ignore_next_arg = False
    for arg in command_args:
        if ignore_next_arg:
            ignore_next_arg = False
        elif arg == '--reference':
            ignore_next_arg = True
        elif not arg.startswith('-'):
            update_paths.append(arg)

    # Get the original pull URL
    command = f"{command_with_options} remote get-url origin"
    retval, pull_url = getstatusoutput(command)
    if retval == 0 and pull_url.startswith(GITCACHE_DIR):
        command = f"{command_with_options} remote get-url --push origin"
        retval, push_url = getstatusoutput(command)
        if retval == 0:
            pull_url = push_url

    if has_init:
        # Handle '--init' part separately by temporarily restoring the original URL
        update_paths_str = ' '.join(update_paths)
        command = f'{called_as_str} {global_options_str} submodule init {update_paths_str}'
        return_value = os.system(command)
        if return_value != 0:
            LOG.error("Initializing submodule with the command %s failed.", command)
            return return_value
        all_args = [i for i in all_args if i != '--init']

    # Make update_paths relative to the checked out repository
    if paths:
        # pylint: disable=no-value-for-parameter
        update_paths = [os.path.relpath(path, os.path.join(*paths)) for path in update_paths]

    # Bugs of the current implementation:
    #  - Relative target URL is not handled correctly in clone.
    command = f"{command_with_options} config -f .gitmodules -l "
    command += "| awk -F '=' '{print $1}' | grep '^submodule' | grep '.url$'"
    retval, output = getstatusoutput(command)
    if retval == 0:
        for tgt_url_key in output.split():
            command = f"{command_with_options} config -f .gitmodules --get {tgt_url_key}"
            retval, tgt_url = getstatusoutput(command)

            if retval != 0:
                continue

            tgt_path_key = tgt_url_key.replace('.url', '.path')
            command = f"{command_with_options} config -f .gitmodules --get {tgt_path_key}"
            retval, tgt_path = getstatusoutput(command)

            if retval != 0:
                continue

            # Skip not specified target paths unless no path is given at all
            if update_paths and tgt_path not in update_paths:
                continue

            if tgt_url.startswith('.') or tgt_url.startswith('/'):
                url_parts = pull_url.split('//')
                url_parts[1] = os.path.normpath(os.path.join(url_parts[1], tgt_url))
                tgt_url = '//'.join(url_parts)

            abs_tgt_path = os.path.join(*paths, tgt_path)
            if os.path.exists(os.path.join(abs_tgt_path, '.git')):
                # Perform a git fetch in the directory...
                command = f"cd {abs_tgt_path}; {called_as_str} fetch"
            else:
                # Perform a git clone into the directory...
                command = f"{called_as_str} {global_options_str} clone {tgt_url} {tgt_path}"

            os.system(command)

    return simple_call_command([config.get("System", "RealGit")] + all_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
