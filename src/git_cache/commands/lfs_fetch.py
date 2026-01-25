# -*- coding: utf-8 -*-
"""
Handler for the git lfs fetch command.

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
from ..database import Database
from ..git_mirror import GitMirror
from ..git_options import GitOptions
from .helpers import get_current_ref, get_mirror_url

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals
def git_lfs_fetch(git_options: GitOptions) -> int:
    """Handle a git lfs fetch command.

    Args:
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    # git lfs fetch [options] [remote [ref...]]
    #  No Mirror Update: git lfs fetch (as it was already updated by other calls)
    #  No Mirror Update: git lfs fetch origin
    #  No Mirror Update: git lfs fetch <other origin>
    #  Mirror Update:    git lfs fetch <options> ... (as the options might include
    #                                                 not-fetched elements)
    #  Mirror Update     git lfs fetch origin ref...
    mirror_url = get_mirror_url(git_options)
    if mirror_url:
        repository = "origin"
        refs = []
        if git_options.command_args:
            repository = git_options.command_args[0]
            refs = git_options.command_args[1:]

        if repository == "origin" and (git_options.command_options or refs):
            if not refs:
                ref = get_current_ref(git_options)
                if ref:
                    refs.append(ref)

            database = Database()
            mirror = GitMirror(url=mirror_url, database=database)
            for ref in refs:
                mirror.fetch_lfs(ref, git_options.command_options)

    return simple_call_command(git_options.get_real_git_all_args())


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
