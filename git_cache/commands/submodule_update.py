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

from .helpers import get_mirror_url, get_pull_url
from ..command_execution import getstatusoutput, simple_call_command

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals,too-many-statements
def git_submodule_update(called_as, git_options):
    """Handle a git submodule update command.

    A 'git submodule update' command is replaced by calling 'git fetch' or
    'git clone' commands for each submodule using the gitcache wrapper. Then
    the real git command is called to fix the configuration.

    If the option '--init' is given, a 'git submodule init' using the
    gitcache wrapper is performed first.

    Args:
        called_as (list):      The arguments used for the command call.
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    called_as_str = ' '.join(called_as)
    global_options_str = ' '.join([f"'{i}'" for i in git_options.global_options])

    cd_paths = git_options.get_global_group_values('run_path')
    update_paths = git_options.command_args

    # If the --init option is specified, we call 'submodule init' first and
    # remove the option for the following commands
    if 'init' in git_options.command_group_values:
        update_paths_str = ' '.join([f"'{i}'" for i in update_paths])
        command = f'{called_as_str} {global_options_str} submodule init {update_paths_str}'
        return_value = os.system(command)
        if return_value != 0:
            LOG.error("Initializing submodule with the command %s failed.", command)
            return return_value
        git_options.all_args = [i for i in git_options.all_args if i != '--init']
        git_options.command_options = [i for i in git_options.command_options if i != '--init']

    # Make update_paths relative to the checked out repository
    if cd_paths:
        # pylint: disable=no-value-for-parameter
        update_paths = [os.path.relpath(path, os.path.join(*cd_paths)) for path in update_paths]

    # Bugs of the current implementation:
    #  - Relative target URL is not handled correctly in clone.
    call_real_git = git_options.get_real_git_with_options()
    command = f"{call_real_git} config -f .gitmodules -l "
    command += "| awk -F '=' '{print $1}' | grep '^submodule' | grep '.url$'"
    retval, output = getstatusoutput(command)
    if retval == 0:
        pull_url = get_mirror_url(git_options)
        if not pull_url:
            pull_url = get_pull_url(git_options)

        for tgt_url_key in output.split():
            command = f"{call_real_git} config -f .gitmodules --get {tgt_url_key}"
            retval, tgt_url = getstatusoutput(command)

            if retval != 0:
                continue

            tgt_path_key = tgt_url_key.replace('.url', '.path')
            command = f"{call_real_git} config -f .gitmodules --get {tgt_path_key}"
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

            abs_tgt_path = os.path.join(*cd_paths, tgt_path)
            if os.path.exists(os.path.join(abs_tgt_path, '.git')):
                # Perform a git fetch in the directory...
                command = f"cd {abs_tgt_path}; {called_as_str} fetch"
            else:
                # Perform a git clone into the directory...
                command = f"{called_as_str} {global_options_str} clone {tgt_url} {tgt_path}"

            os.system(command)

    return simple_call_command(git_options.get_real_git_all_args())


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
