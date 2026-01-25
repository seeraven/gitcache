# -*- coding: utf-8 -*-
"""
Handler for the git update-mirrors command.

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

from ..database import Database
from ..git_mirror import GitMirror

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def git_update_all_mirrors() -> int:
    """Handle a git update-mirrors command.

    Return:
        Returns 0 on success, otherwise 1.
    """
    LOG.info("Starting update of all known mirrors.")
    database = Database()
    failed = []
    success = []
    for path in sorted(database.get_all().keys()):
        mirror = GitMirror(path=path, database=database)
        if mirror.update(force=True):
            success.append(path)
        else:
            failed.append(path)

    if success:
        LOG.info("Updated the following paths successfully:")
        for path in success:
            LOG.info("  %s", path)

    if failed:
        LOG.error("Failed to update the following paths:")
        for path in failed:
            LOG.error("  %s", path)

        return 1

    if not success and not failed:
        LOG.warning("Nothing to update.")

    return 0


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
