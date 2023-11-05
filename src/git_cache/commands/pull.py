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

from ..command_execution import pretty_call_command_retry
from ..config import Config
from ..database import Database
from ..git_mirror import GitMirror
from .helpers import get_current_ref, get_mirror_url

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals
def git_pull(git_options):
    """Handle a git pull command.

    Args:
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    action = "Update"
    config = Config()

    repository = "origin"
    refs = []
    if git_options.command_args:
        repository = git_options.command_args[0]
        refs = git_options.command_args[1:]

    mirror_url = get_mirror_url(git_options)
    if mirror_url and repository == "origin":
        database = Database()
        mirror = GitMirror(url=mirror_url, database=database)
        mirror.update()
        database.increment_counter(mirror.path, "updates")

        # The mirror.update() updates the LFS data of the default ref of
        # the mirror repository, which should be 'master' or 'main'. If we
        # are currently on a different branch, we want to update that branch
        # as well.
        if not refs:
            refs.append(get_current_ref(git_options))
        default_ref = mirror.get_default_ref()
        for ref in refs:
            if ref and ref != default_ref:
                mirror.fetch_lfs(ref)

        config = mirror.config
        action = f"Update from mirror {mirror.path}"

    return_code, _, _ = pretty_call_command_retry(
        action,
        "",
        git_options.get_real_git_all_args(),
        num_retries=config.get("Update", "Retries"),
        command_timeout=config.get("Update", "CommandTimeout"),
        output_timeout=config.get("Update", "OutputTimeout"),
    )

    return return_code


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
