"""
Module for handling the global settings of gitcache.

The global settings can't be retrieved from the config.Config class as they
are not known in advance or not customizable.

Attributes:
    GITCACHE_DIR (str): The base directory for hosting all gitcache related information
        including the mirrors.

        The value is retrieved from the environment variable :code:`GITCACHE_DIR`. If this
        variable does not exist, the default value :code:`~/.gitcache` is used.

    GITCACHE_DB (str): The database file.

    GITCACHE_DB_LOCK (str): The database lock file.

    GITCACHE_LOGLEVEL (str): The log level of gitcache, e.g., 'INFO' or 'DEBUG'.

        The value is retrieved from the environment variable :code:`GITCACHE_LOGLEVEL`. If this
        variable does not exist, the default value :code:`INFO` is used.

    GITCACHE_LOGFORMAT (str): The log format of gitcache.

        The value is retrieved from the environment variable :code:`GITCACHE_LOGFORMAT`. If this
        variable does not exist, the default value :code:`%(asctime)s %(message)s` is used.

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
import os

# -----------------------------------------------------------------------------
# Settings
# -----------------------------------------------------------------------------
GITCACHE_DIR = os.getenv("GITCACHE_DIR", os.path.join(os.getenv("HOME", "/"), ".gitcache"))
GITCACHE_DB = os.path.join(GITCACHE_DIR, "db")
GITCACHE_DB_LOCK = os.path.join(GITCACHE_DIR, "db.lock")
GITCACHE_LOGLEVEL = os.getenv("GITCACHE_LOGLEVEL", "INFO")
GITCACHE_LOGFORMAT = os.getenv("GITCACHE_LOGFORMAT", "%(asctime)s %(message)s")


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
