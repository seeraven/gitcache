# -*- coding: utf-8 -*-
"""
Handler for the git submodule init command.

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
from ..global_settings import GITCACHE_DIR


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def git_submodule_init(all_args, global_options):
    """Handle a git submodule init command.

    Args:
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

    command = "%s remote get-url origin" % command_with_options
    retval, pull_url = getstatusoutput(command)
    if retval == 0 and pull_url.startswith(GITCACHE_DIR):
        command = "%s remote get-url --push origin" % command_with_options
        retval, push_url = getstatusoutput(command)
        if retval == 0:
            command = "%s remote set-url origin %s" % (command_with_options,
                                                       push_url)
            retval, _ = getstatusoutput(command)

            if retval == 0:
                retval = simple_call_command([config.get("System", "RealGit")] + all_args)
            else:
                LOG.warning("Can't restore original pull URL of the repository!")

            command = "%s remote set-url origin %s;" % (command_with_options,
                                                        pull_url)
            command += "%s remote set-url --push origin %s" % (command_with_options,
                                                               push_url)
            _, _ = getstatusoutput(command)
            return retval

        LOG.warning("Can't get push URL of the repository!")
    else:
        LOG.debug("Repository is not managed by gitcache!")

    # Fallback to original git
    return simple_call_command([config.get("System", "RealGit")] + all_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
