# -*- coding: utf-8 -*-
"""
Handler for the git cleanup command.

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
def git_cleanup() -> int:
    """Handle a git cleanup command.

    Return:
        Returns 0 on success, otherwise 1.
    """
    LOG.info("Starting cleanup of mirrors.")
    database = Database()
    num_removed = 0
    for path in sorted(database.get_all().keys()):
        mirror = GitMirror(path=path, database=database)
        if mirror.cleanup():
            LOG.info("Removed mirror %s.", path)
            num_removed += 1
    LOG.info("Removed %d mirrors.", num_removed)
    return 0


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
