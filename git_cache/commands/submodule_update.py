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


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals
def git_submodule_update(called_as, all_args, global_options):
    """Handle a git submodule update command.

    Args:
        called_as (list):      The arguments used for the command call.
        all_args (list):       All arguments to the 'git' command.
        global_options (list): The options given to git, not the command.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    config = Config()

    global_options_str = ' '.join(["'%s'" % i for i in global_options])
    command_with_options = "%s %s" % (config.get("System", "RealGit"),
                                      global_options_str)

    # Translate all '-C' options into a list of 'cd' commands
    paths = []
    save_next_path = False
    for arg in global_options:
        if save_next_path:
            paths.append(arg)
            save_next_path = False
        elif arg == '-C':
            save_next_path = True

    command = "%s config -f .gitmodules -l " % command_with_options
    command += "| awk -F '=' '{print $1}' | grep '^submodule' | grep '.url$'"
    retval, output = getstatusoutput(command)
    if retval == 0:
        for tgt_url_key in output.split():
            command = "%s config -f .gitmodules --get %s" % (command_with_options, tgt_url_key)
            retval, tgt_url = getstatusoutput(command)

            if retval != 0:
                continue

            tgt_path_key = tgt_url_key.replace('.url', '.path')
            command = "%s config -f .gitmodules --get %s" % (command_with_options, tgt_path_key)
            retval, tgt_path = getstatusoutput(command)

            if retval != 0:
                continue

            abs_tgt_path = os.path.join(*paths, tgt_path)
            if os.path.exists(os.path.join(abs_tgt_path, '.git')):
                # Perform a git fetch in the directory...
                command = "cd %s; %s fetch" % (abs_tgt_path, ' '.join(called_as))
            else:
                # Perform a git clone into the directory...
                command = "%s %s clone %s %s" % (' '.join(called_as), global_options_str,
                                                 tgt_url, tgt_path)

            os.system(command)

    return simple_call_command([config.get("System", "RealGit")] + all_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
