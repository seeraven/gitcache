# -*- coding: utf-8 -*-
"""
Handler for the git delete-mirror command.

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
from typing import List

from ..database import Database
from ..git_mirror import GitMirror

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def git_delete_mirror(mirror_list: List[str]) -> int:
    """Handle a git delete-mirror command.

    Args:
        mirror_list (list): The mirrors identified by path or url to delete.

    Return:
        Returns 0 on success, otherwise 1.
    """
    database = Database()
    db_map = database.get_all()
    known_urls = []
    for _, entry in db_map.items():
        known_urls.append(entry["url"])

    num_deleted = 0
    num_failed = 0
    LOG.info("Deleting specified mirrors.")
    for mirror_url in mirror_list:
        if mirror_url in known_urls:
            mirror = GitMirror(url=mirror_url, database=database)
        elif mirror_url in db_map:
            mirror = GitMirror(path=mirror_url, database=database)
        else:
            LOG.error("Unknown mirror %s (does not match any known URL or mirror path).", mirror_url)
            num_failed += 1
            continue
        mirror.delete()
        LOG.info("Deleted mirror %s.", mirror.path)
        num_deleted += 1

    if num_deleted == 0:
        LOG.warning("No mirror deleted.")
    elif num_deleted == 1:
        LOG.info("Mirror deleted.")
    else:
        LOG.info("%d mirrors deleted.", num_deleted)

    if num_failed != 0:
        LOG.warning("%d mirror(s) not identified!", num_failed)

    return 0 if num_failed == 0 else 1


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
