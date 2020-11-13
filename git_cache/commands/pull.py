# -*- coding: utf-8 -*-
"""
Handler for the git pull command.

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
# pylint: disable=too-many-locals
def git_pull(all_args, global_options):
    """Handle a git pull command.

    Args:
        all_args (list):       All arguments to the 'git' command.
        global_options (list): The options given to git, not the command.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    action = "Update"
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
            database = Database()
            mirror = GitMirror(url=push_url, database=database)
            mirror.update()
            database.increment_counter(mirror.path, "updates")

            # The mirror.update() updates the LFS data of the default ref of
            # the mirror repository, which should be 'master' or 'main'. If we
            # are currently on a different branch, we want to update that branch
            # as well.
            command = "%s rev-parse --abbrev-ref HEAD" % command_with_options
            retval, ref = getstatusoutput(command)
            if retval == 0 and ref != mirror.get_default_ref():
                mirror.fetch_lfs(ref)

            config = mirror.config
            action = "Update from mirror %s" % mirror.path
        else:
            LOG.warning("Can't get push URL of the repository!")
    else:
        LOG.debug("Repository is not managed by gitcache!")

    original_command_args = [config.get("System", "RealGit")] + all_args

    return_code, _, _ = pretty_call_command_retry(
        action,
        '',
        ' '.join(["'%s'" % i for i in original_command_args]),
        num_retries=config.get("Update", "Retries"),
        command_timeout=config.get("Update", "CommandTimeout"),
        output_timeout=config.get("Update", "OutputTimeout"))

    return return_code


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
