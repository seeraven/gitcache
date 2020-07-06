# -*- coding: utf-8 -*-
"""
A single git mirror handler.

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
import os
import shutil

import portalocker

from .command_execution import pretty_call_command_retry
from .config import Config
from .database import Database
from .global_settings import GITCACHE_DIR


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Class Definitions
# -----------------------------------------------------------------------------
class Locker:
    """A lock for the mirror."""

    def __init__(self, name, filename, config):
        """Construct a new lock object for the mirror.

        Args:
            name (str):     The name of the item that is locked.
            filename (str): The lock file.
            config (obj):   The config.Config object to get the settings.
        """
        self.name = name
        self.lock = portalocker.Lock(filename)
        self.warn_after = config.get("Command", "WarnIfLockedFor")
        self.check_interval = config.get("Command", "CheckInterval")
        self.timeout = config.get("Command", "LockTimeout")

    def __enter__(self):
        """Aquire the lock."""
        try:
            return self.lock.acquire(timeout=self.warn_after)
        except portalocker.exceptions.LockException:
            pass

        LOG.info("%s is locked. Waiting up to %d seconds.", self.name, self.timeout)
        return self.lock.acquire(timeout=self.timeout, check_interval=self.check_interval)

    def __exit__(self, type_, value, traceback):
        """Release the lock."""
        self.lock.release()


class GitMirror:
    """This class represents a git mirror identified by the path.

    The git mirror is put in a subdirectory under GITCACHE_DIR constructed from
    the URL of the upstream repository. Under this directory the following items
    are stored:

      - The lockfile to lock the mirror.
      - The git mirror.
      - git-lfs storage directory used if the setting LFS/PerMirrorStorage is
        set to True.

    Attributes:
       url (str):           The upstream URL.
       path (str):          The path of the mirror.
       git_dir (str):       The path to the git data directory.
       git_lfs_dir (str):   The path to the git-lfs storage directory.
       lockfile (str):      The path of the lockfile.
       configfile (str):    The path of the per-mirror config file.
       config (obj):        The config.Config object for this mirror created by loading
                            the global config file and the per-mirror config file.
       database (obj):      The database.Database to use for repository meta information.
    """

    def __init__(self, url=None, path=None, database=None):
        """Construct a new GitMirror object.

        Args:
            url (str):      The upstream url.
            path (str):     The path of the mirror.
            database (obj): The database to use. If not given, a local database
                            will be used.
        """
        self.url = url
        self.path = path

        self.database = database
        if self.database is None:
            self.database = Database()

        if self.url and self.path is None:
            self.path = self.url_to_path(self.url)

        if self.path and self.url is None:
            self.url = self.database.get_url_for_path(self.path)

        self.git_dir = os.path.join(self.path, "git")
        self.git_lfs_dir = os.path.join(self.path, "lfs")
        self.lockfile = os.path.join(self.path, "lock")
        self.configfile = os.path.join(self.path, "gitcache.config")
        os.makedirs(self.git_lfs_dir, exist_ok=True)

        self.config = Config()
        self.config.load(self.configfile)

    def update(self, ref='master', force=False):
        """Update or create the mirror.

        If the mirror path does not exist, a bare mirror is created.

        If the mirror path exists, the mirror is updated if the last update was
        not performed within the last n seconds.

        Args:
            ref (str):    The ref to use for the fetch of the lfs data.
            force (bool): If set to True, the mirror is updated even if the
                          update interval is not yet reached.

        Return:
            Returns True if the mirror was updated or False if the request timed out.
        """
        try:
            with Locker("Mirror %s" % self.path, self.lockfile, self.config):
                if not os.path.exists(self.git_dir):
                    return self._clone(ref)

                if force or self._update_time_reached():
                    return self._update(ref)

                LOG.info("Update time of mirror %s not reached yet.", self.path)
        except portalocker.exceptions.LockException:
            LOG.error("Update timed out due to locked mirror.")
            return False
        return True

    def fetch_lfs(self, ref, options=None):
        """Fetch the lfs data of the specified ref for the mirror.

        Args:
            ref (str):      The ref to use for the fetch of the lfs data.
            options (list): Options of the git lfs fetch call.

        Return:
            Returns True if the lfs fetch was successful.
        """
        try:
            with Locker("Mirror %s" % self.path, self.lockfile, self.config):
                return self._fetch_lfs(ref, options)
        except portalocker.exceptions.LockException:
            LOG.error("LFS fetch of %s timed out due to locked mirror.", ref)
            return False
        return True

    def cleanup(self):
        """Delete the mirror if it is too old.

        Return:
            Returns True if the mirror was deleted.
        """
        if self._cleanup_time_reached():
            LOG.debug("Mirror %s is too old. Removing it.", self.path)
            return self.delete()
        return False

    def delete(self):
        """Delete the mirror.

        Return:
            Returns True if the mirror was deleted or False if the request timed out.
        """
        try:
            with Locker("Mirror %s" % self.path, self.lockfile, self.config):
                LOG.debug("Deleting mirror %s", self.path)
                shutil.rmtree(self.path, ignore_errors=True)
                self.database.remove(self.path)
        except portalocker.exceptions.LockException:
            LOG.error("Delete timed out due to locked mirror.")
            return False
        return True

    def clone_from_mirror(self, original_args, ref):
        """Clone from the mirror.

        Args:
            original_args (list): The original arguments to git (without 'git') including
                                  the 'clone' command.
            ref (str):            The ref to use for the fetch of the lfs data.

        Return:
            Returns the return code of the last command.
        """
        if not self.update(ref):
            return 1

        git_lfs_url = self.url + "/info/lfs"

        new_args = [x if x != self.url else self.git_dir for x in original_args]
        new_args.insert(0, self.config.get("System", "RealGit"))
        new_args.insert(1, "-c")
        new_args.insert(2, "lfs.url=%s" % git_lfs_url)
        if self.config.get('LFS', 'PerMirrorStorage'):
            new_args.insert(3, "-c")
            new_args.insert(4, "lfs.storage=%s" % self.git_lfs_dir)

        target_dir = original_args[-1]
        if target_dir == self.url:
            target_dir = os.path.basename(self.url).replace('.git', '')
            new_args.append(target_dir)

        return_code, _, _ = pretty_call_command_retry(
            'Clone from mirror %s' % self.path,
            '',
            ' '.join(["'%s'" % i for i in new_args]),
            num_retries=self.config.get("Clone", "Retries"),
            command_timeout=self.config.get("Clone", "CommandTimeout"),
            output_timeout=self.config.get("Clone", "OutputTimeout"),
            remove_dir=target_dir)

        if return_code != 0:
            return return_code

        self.database.increment_counter(self.path, "clones")

        # Translate all '-C' options into a list of 'cd' commands
        paths = []
        save_next_path = False
        for arg in original_args:
            if save_next_path:
                paths.append(arg)
                save_next_path = False
            elif arg == '-C':
                save_next_path = True
            elif arg == 'clone':
                break
        paths.append(target_dir)

        LOG.info("Setting push URL to %s and configure LFS.", self.url)
        command = ';'.join(["cd %s" % x for x in paths])
        command += ";%s remote set-url --push origin %s" % (self.config.get("System", "RealGit"),
                                                            self.url)
        command += ";%s config --local lfs.url %s" % (self.config.get("System", "RealGit"),
                                                      git_lfs_url)
        if self.config.get('LFS', 'PerMirrorStorage'):
            command += ";%s config --local lfs.storage %s" % (self.config.get("System", "RealGit"),
                                                              self.git_lfs_dir)

        return os.system(command)

    def _update_time_reached(self):
        """Check if the update time of the mirror is reached.

        Return:
            Returns True if the mirror should be updated.
        """
        update_interval = self.config.get("MirrorHandling", "UpdateInterval")
        if update_interval < 0:
            return False

        return self.database.get_time_since_last_update(self.path) >= update_interval

    def _cleanup_time_reached(self):
        """Check if the mirror should be removed due to inactivity.

        Return:
            Returns True if the mirror should be removed.
        """
        return (self.database.get_time_since_last_update(self.path) >=
                self.config.get("MirrorHandling", "CleanupAfter"))

    def _clone(self, ref='master'):
        """Clone the mirror.

        Args:
            ref (str): The ref to use for the fetch of the lfs data.

        Return:
            Returns True on success.
        """
        command = "%s clone --progress --mirror %s %s" % (self.config.get("System", "RealGit"),
                                                          self.url,
                                                          self.git_dir)
        return_code, _, _ = pretty_call_command_retry(
            'Initial clone of %s into %s' % (self.url, self.path),
            '',
            command,
            num_retries=self.config.get("Clone", "Retries"),
            command_timeout=self.config.get("Clone", "CommandTimeout"),
            output_timeout=self.config.get("Clone", "OutputTimeout"),
            remove_dir=self.git_dir)

        if return_code == 0:
            self.database.add(self.url, self.path)
        else:
            return False

        return self._fetch_lfs(ref)

    def _update(self, ref='master', handle_gc_error=True):
        """Update the mirror.

        Args:
            ref (str):              The ref to use for the fetch of the lfs data.
            handle_gc_error (bool): If set to True, garbage collection errors are detected
                                    and handled.

        Return:
            Returns True on success.
        """
        command = "cd %s; %s remote update --prune" % (self.git_dir,
                                                       self.config.get("System", "RealGit"))
        return_code, _, _ = pretty_call_command_retry(
            'Update of %s' % self.path,
            'garbage collection error',
            command,
            num_retries=self.config.get("Update", "Retries"),
            command_timeout=self.config.get("Update", "CommandTimeout"),
            output_timeout=self.config.get("Update", "OutputTimeout"),
            abort_on_pattern=b'remove gc.log' if handle_gc_error else None)

        if return_code == 0:
            self.database.save_update_time(self.path)
        elif handle_gc_error and return_code == -3000:
            if self._run_gc():
                return self._update(ref, False)
            return False
        else:
            return False

        return self._fetch_lfs(ref)

    def _run_gc(self):
        """Run the garbage collection.

        Return:
            Returns True on success.
        """
        command = "cd %s; %s gc && rm -f gc.log" % (self.git_dir,
                                                    self.config.get("System", "RealGit"))
        return_code, _, _ = pretty_call_command_retry(
            'Garbage collection on %s' % self.path,
            '',
            command,
            num_retries=self.config.get("GC", "Retries"),
            command_timeout=self.config.get("GC", "CommandTimeout"),
            output_timeout=self.config.get("GC", "OutputTimeout"))

        return return_code == 0

    def _fetch_lfs(self, ref, options=None):
        """Fetch the lfs data of the specified ref.

        Args:
            ref (str):      The ref to use for the fetch of the lfs data.
            options (list): Options of the git lfs fetch call.

        Return:
            Returns True if the lfs fetch was successful.
        """
        git_options = ""
        if self.config.get('LFS', 'PerMirrorStorage'):
            git_options = "-c lfs.storage=%s" % self.git_lfs_dir
        command = "cd %s; %s %s lfs fetch %s origin %s" % (self.git_dir,
                                                           self.config.get("System", "RealGit"),
                                                           git_options,
                                                           ' '.join(options) if options else '',
                                                           ref)

        return_code, _, _ = pretty_call_command_retry(
            'LFS fetch of ref %s from %s into %s' % (ref, self.url, self.path),
            '',
            command,
            num_retries=self.config.get("LFS", "Retries"),
            command_timeout=self.config.get("LFS", "CommandTimeout"),
            output_timeout=self.config.get("LFS", "OutputTimeout"))

        return return_code == 0

    @staticmethod
    def url_to_path(url):
        """Convert an URL into a repository mirror path.

        Args:
            url (str): The URL of the repository.

        Return:
            Returns the mirror path or None if the url can't be converted.
        """
        if url.startswith('http://') or url.startswith('https://'):
            sub_dir = url.split('//')[1]
            if '@' in sub_dir:
                sub_dir = sub_dir.split('@')[1]
            if ':' in sub_dir:
                sub_dir = sub_dir.replace(':', '_')
            if sub_dir.endswith('.git'):
                sub_dir = sub_dir[:-4]
            if sub_dir.endswith('/'):
                sub_dir = sub_dir[:-1]
            return os.path.join(GITCACHE_DIR, "mirrors", sub_dir)

        # URL is already a path
        if url.startswith(GITCACHE_DIR):
            return url

        return None


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
