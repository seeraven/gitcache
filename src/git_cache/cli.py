"""
Module containing the main entry point of gitcache.

Copyright:
    2024 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging
import os
import sys

import coloredlogs

from .git_cache_command import git_cache
from .git_command import handle_git_command
from .global_settings import GITCACHE_LOGFORMAT, GITCACHE_LOGLEVEL


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main_cli() -> None:
    """The main entry point of the gitcache command."""
    log_level_styles = {
        "debug": {"color": "cyan"},
        "info": {"color": "green"},
        "warning": {"color": "yellow"},
        "error": {"color": "red"},
        "critical": {"bold": True, "color": "red"},
    }
    coloredlogs.install(level=GITCACHE_LOGLEVEL, level_styles=log_level_styles, fmt=GITCACHE_LOGFORMAT)

    logger = logging.getLogger(__name__)
    logger.debug("Python executable: %s", sys.executable)
    logger.debug("Called as %s", sys.argv)

    # If using an interpreter we add it as the first argument of the "called_as" array.
    called_as_base = []
    if not getattr(sys, "frozen", False):
        called_as_base.append(sys.executable)

    git_names = ["git", "git.exe"]
    if os.path.basename(sys.argv[0]) in git_names:
        # Called as "git ..."
        handle_git_command(called_as_base + sys.argv[0:1], sys.argv[1:])
    elif len(sys.argv) > 1 and os.path.basename(sys.argv[1]) in git_names:
        # Called as "gitcache git ..."
        handle_git_command(called_as_base + sys.argv[0:2], sys.argv[2:])
    else:
        sys.exit(0 if git_cache() else 1)
