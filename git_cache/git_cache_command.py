# -*- coding: utf-8 -*-
"""
Module for handling the call of gitcache.

Attributes:
    DESCRIPTION (str): The usage description of the main parser.

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
import argparse
import logging

from .commands.cleanup import git_cleanup
from .commands.delete import git_delete_mirror
from .commands.update_all import git_update_all_mirrors
from .config import Config
from .database import Database
from .global_settings import GITCACHE_DB, GITCACHE_DB_LOCK, GITCACHE_DIR


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
DESCRIPTION = """
gitcache
========

Local cache for git repositories to speed up working with large repositories
and multiple clones.

Without any arguments, this command prints the current configuration. Using
the listed options below, the output can be changed and special actions can
be triggered.

If called with the first argument 'git' or when called as 'git' using a symlink,
it acts as a wrapper for the git command and intercepts the commands required
for the mirror handling.
"""


# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
def get_parser():
    """Get the argument parser for the :code:`gitcache` command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-c", "--cleanup",
                        help="Remove all outdated repositories.",
                        action="store_true",
                        default=False)
    parser.add_argument("-u", "--update-all",
                        help="Update all mirrors.",
                        action="store_true",
                        default=False)
    parser.add_argument("-d", "--delete",
                        metavar="MIRROR",
                        help="Delete a mirror identified by its URL or its path in the cache. "
                        "This option can be specified multiple times.",
                        action="append",
                        default=[])
    parser.add_argument("-s", "--show-statistics",
                        help="Show the statistics.",
                        action="store_true",
                        default=False)
    parser.add_argument("-z", "--zero-statistics",
                        help="Clear the statistics.",
                        action="store_true",
                        default=False)
    return parser


def git_cache():
    """Execute the main function if called as :code:`gitcache`.

    Return:
        Returns True on success, otherwise False.
    """
    parser = get_parser()
    args = parser.parse_args()
    success = True

    if args.cleanup:
        success = git_cleanup() == 0

    if args.update_all:
        success = git_update_all_mirrors() == 0

    if args.delete:
        success = git_delete_mirror(args.delete) == 0

    if args.zero_statistics:
        database = Database()
        for path in database.get_all():
            database.clear_counters(path)
        LOG.info("Statistics cleared.")

    if args.show_statistics:
        all_records = Database().get_all()
        total_mirror_updates = 0
        total_clones = 0
        total_updates = 0

        for path in sorted(all_records):
            print("Mirror of %s:" % all_records[path]["url"])
            print("  Mirror Updates:      %d" % all_records[path]["mirror-updates"])
            print("  Clones from Mirror:  %d" % all_records[path]["clones"])
            print("  Updates from Mirror: %d" % all_records[path]["updates"])
            print()
            total_mirror_updates += all_records[path]["mirror-updates"]
            total_clones += all_records[path]["clones"]
            total_updates += all_records[path]["updates"]

        print("Total:")
        print("  Mirror Updates:      %d" % total_mirror_updates)
        print("  Clones from Mirror:  %d" % total_clones)
        print("  Updates from Mirror: %d" % total_updates)
        print()

    elif not (args.cleanup or args.update_all or args.delete or args.zero_statistics):
        print("gitcache global settings:")
        print("-------------------------")
        print("  GITCACHE_DIR      = %s" % GITCACHE_DIR)
        print("  GITCACHE_DB       = %s" % GITCACHE_DB)
        print("  GITCACHE_DB_LOCK  = %s" % GITCACHE_DB_LOCK)
        print()
        print("gitcache configuration:")
        print("-----------------------")
        config = Config()
        print(config)

    return success


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
