# -*- coding: utf-8 -*-
"""
The gitcache database.

The gitcache database is stored on disc and contains a map of repository paths
to the meta information for the repositories.

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
import json
import os
import time
from typing import Any, Dict, Optional

import portalocker

from .global_settings import GITCACHE_DB, GITCACHE_DB_LOCK, GITCACHE_DIR


# -----------------------------------------------------------------------------
# Class Definitions
# -----------------------------------------------------------------------------
class Database:
    """Database containing all mirrored repositories along with their meta information.

    The database is stored as a map with entries for each repository mirror path
    containing the following key-value pairs:

      - :code:`url` with the upstream URL
      - :code:`last-update-time` with the time of the last mirror update.
      - :code:`mirror-updates` as a counter of the number of updates of the mirror.
      - :code:`lfs-updates` as a counter of the number of lfs-updates of the mirror.
      - :code:`clones` as a counter of the number of clones from the mirror.
      - :code:`updates` as a counter of the number of updates from the mirror.

    Attributes:
        database (map): A map of repository paths to the per-repository entries.
    """

    def __init__(self) -> None:
        """Construct a new Database object."""
        self.database: Dict[str, Dict[str, Any]] = {}
        os.makedirs(GITCACHE_DIR, exist_ok=True)

    def add(self, url: str, path: str) -> None:
        """Add a new entry to the database.

        Args:
            url (str):  The upstream repository URL.
            path (str): The path of the repository mirror.
        """
        with portalocker.Lock(GITCACHE_DB_LOCK):
            self._load()
            self.database[path] = {
                "url": url,
                "last-update-time": time.time(),
                "mirror-updates": 0,
                "lfs-updates": 0,
                "clones": 0,
                "updates": 0,
            }
            self._save()

    def remove(self, path: str) -> None:
        """Remove an entry from the database.

        Args:
            path (str): The path of the repository mirror.
        """
        with portalocker.Lock(GITCACHE_DB_LOCK):
            self._load()
            del self.database[path]
            self._save()

    def save_update_time(self, path: str) -> None:
        """Save the current time as the last-update-time of the mirror.

        Args:
            path (str): The path of the repository mirror.
        """
        with portalocker.Lock(GITCACHE_DB_LOCK):
            self._load()
            self.database[path]["last-update-time"] = time.time()
            self.database[path]["mirror-updates"] = self.database[path]["mirror-updates"] + 1
            self._save()

    def increment_counter(self, path: str, counter: str) -> None:
        """Increment a counter of a mirror.

        Args:
            path (str):    The path of the repository mirror.
            counter (str): The counter to increment. Use one of 'mirror-updates', 'lfs-updates',
                           'clones' or 'updates'.
        """
        with portalocker.Lock(GITCACHE_DB_LOCK):
            self._load()
            self.database[path][counter] = self.database[path][counter] + 1
            self._save()

    def clear_counters(self, path: str) -> None:
        """Clear all counters of a mirror.

        Args:
            path (str):    The path of the repository mirror.
        """
        with portalocker.Lock(GITCACHE_DB_LOCK):
            self._load()
            for counter in ["mirror-updates", "lfs-updates", "clones", "updates"]:
                self.database[path][counter] = 0
            self._save()

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get the whole database.

        Return:
            Returns the whole database.
        """
        with portalocker.Lock(GITCACHE_DB_LOCK):
            self._load()

        return self.database

    def get(self, path: str) -> Optional[Dict[str, Any]]:
        """Get the database entry for the given repository path.

        Args:
            path (str): The path of the repository mirror.

        Return:
            Returns the database entry for the given path or None if the specified
            path is not in the database.
        """
        self.get_all()

        if path in self.database:
            return self.database[path]

        return None

    def get_url_for_path(self, path: str) -> Optional[str]:
        """Get the url for the given path.

        Args:
            path (str): The path of the repository mirror.

        Return:
            Returns the url of the mirror or None if the specified
            path is not in the database.
        """
        entry = self.get(path)
        if entry:
            return entry["url"]
        return None

    def get_time_since_last_update(self, path: str) -> float:
        """Get the time in seconds since the last update for the given repository path.

        Args:
            path (str): The path of the repository mirror.

        Return:
            Returns the time in seconds since the last update.
        """
        entry = self.get(path)
        if entry:
            return time.time() - entry["last-update-time"]
        return 0.0

    def _load(self) -> None:
        """Load the database from disc."""
        self.database = {}

        if os.path.exists(GITCACHE_DB):
            with open(GITCACHE_DB, "r", encoding="utf-8") as handle:
                database = json.load(handle)
                for path in database:
                    database[path].setdefault("lfs-updates", 0)

                # Internal database uses absolute paths
                for key, entry in database.items():
                    if not os.path.isabs(key):
                        path = os.path.normpath(os.path.join(GITCACHE_DIR, key))
                    else:
                        path = key
                    self.database[path] = entry

    def _save(self) -> None:
        """Save the database to disc."""
        # Convert keys to relative paths
        database = {}
        for key, entry in self.database.items():
            database[os.path.relpath(key, GITCACHE_DIR)] = entry

        with open(GITCACHE_DB, "w", encoding="utf-8") as handle:
            json.dump(database, handle)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
