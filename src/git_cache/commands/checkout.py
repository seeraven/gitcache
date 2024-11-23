# -*- coding: utf-8 -*-
"""
Handler for the git checkout command.

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
from ..database import Database
from ..git_mirror import GitMirror
from ..git_options import GitOptions
from .helpers import get_mirror_url

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-many-locals
def git_checkout(git_options: GitOptions) -> int:
    """Handle a git checkout command.

    Args:
        git_options (obj):     The GitOptions object.

    Return:
        Returns 0 on success, otherwise the return code of the last failed
        command.
    """
    # Collect all refs for an lfs fetch
    ref_candidates = [x for x in git_options.command_args if not x.startswith("-") and not x.startswith(":")]
    lfs_fetch_refs = []
    for ref in ref_candidates:
        command = git_options.get_real_git_with_options()
        command += ["show-ref", ref]
        retval, output = getstatusoutput(command)
        if retval == 0 and "remotes" in output:
            lfs_fetch_refs.append(ref)

    if lfs_fetch_refs:
        mirror_url = get_mirror_url(git_options)
        if mirror_url:
            database = Database()
            mirror = GitMirror(url=mirror_url, database=database)
            for ref in lfs_fetch_refs:
                mirror.fetch_lfs(ref)

    return simple_call_command(git_options.get_real_git_all_args())


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
