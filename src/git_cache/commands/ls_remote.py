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

from ..command_execution import simple_call_command
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
# pylint: disable=too-many-locals
def git_ls_remote(git_options):
    """Handle a git ls-remote command.

    The git ls-remote command updates the mirror if no repository is specified
    or the repository 'origin' is specified. After the update, the command
    is rewritten to use the mirror.

    Args:
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    config = Config()
    repository = None
    mirror_url = None

    if git_options.command_args:
        repository = git_options.command_args[0]

    if repository is None or repository == "origin":
        mirror_url = get_mirror_url(git_options)

    supported_prefixes = ["http://", "https://", "ssh://"]
    if repository and any(repository.startswith(prefix) for prefix in supported_prefixes):
        if use_mirror_for_remote_url(repository):
            mirror_url = repository

    if mirror_url:
        database = Database()
        mirror = GitMirror(url=mirror_url, database=database)
        mirror.update()
        new_args = git_options.global_options
        new_args += [git_options.command]
        new_args += git_options.command_options
        new_args += ["origin"]
        new_args += git_options.command_args[1:]
    else:
        new_args = git_options.all_args

    original_command_args = [config.get("System", "RealGit")] + new_args
    return simple_call_command(original_command_args)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
