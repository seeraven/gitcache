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

from ..command_execution import pretty_call_command_retry, simple_call_command
from ..config import Config
from ..database import Database
from ..git_mirror import GitMirror
from .helpers import get_mirror_url, use_mirror_for_remote_url

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals,too-many-statements
def git_fetch(git_options):
    """Handle a git fetch command.

    Args:
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    config = Config()
    real_git = config.get("System", "RealGit")

    remote_url = None
    mirror_path = None
    if git_options.command_args:
        for arg in git_options.command_args:
            mirror_path = GitMirror.get_mirror_path(arg)
            if mirror_path:
                remote_url = arg
                break

    if remote_url is None:
        remote_url = get_mirror_url(git_options)
    elif not use_mirror_for_remote_url(remote_url):
        remote_url = None

    if remote_url:
        database = Database()
        mirror = GitMirror(url=remote_url, database=database)
        mirror.update()
        database.increment_counter(mirror.path, "updates")
        config = mirror.config
        action = f"Fetch from mirror {mirror.path}"
        new_args = [x if x != remote_url else mirror.git_dir for x in git_options.all_args]

        # We configure the LFS storage here to support the Jenkins way
        # of cloning git repositories.
        LOG.info("Configuring LFS.")
        command = [real_git, "config", "--local", "lfs.url", f"{mirror.url}/info/lfs"]
        simple_call_command(command, cwd=git_options.get_run_path())

        if config.get("LFS", "PerMirrorStorage"):
            command = [real_git, "config", "--local", "lfs.storage", mirror.git_lfs_dir]
            simple_call_command(command, cwd=git_options.get_run_path())

        # Try the fetch command in the checkout once.
        original_command_args = [real_git] + new_args
        return_code, _, _ = pretty_call_command_retry(
            action,
            "",
            original_command_args,
            num_retries=1,
            command_timeout=config.get("Update", "CommandTimeout"),
            output_timeout=config.get("Update", "OutputTimeout"),
        )
        if return_code == 0:
            return return_code

        # Try the command in the mirror, using the same command arguments (ignoring the options).
        mirror.fetch(git_options.command_args)

    else:
        action = "Fetch"
        new_args = git_options.all_args

    original_command_args = [real_git] + new_args

    return_code, _, _ = pretty_call_command_retry(
        action,
        "",
        original_command_args,
        num_retries=config.get("Update", "Retries"),
        command_timeout=config.get("Update", "CommandTimeout"),
        output_timeout=config.get("Update", "OutputTimeout"),
    )

    return return_code


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
