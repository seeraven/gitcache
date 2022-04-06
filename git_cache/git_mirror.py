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

from .command_execution import getstatusoutput, pretty_call_command_retry, simple_call_command
from .config import Config, has_git_lfs_cmd
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

    def update(self, ref=None, force=False):
        """Update or create the mirror.

        If the mirror path does not exist, a bare mirror is created.

        If the mirror path exists, the mirror is updated if the last update was
        not performed within the last n seconds.

        Args:
            ref (str):    The ref to use for the fetch of the lfs data. If None,
                          the default branch is determined and used.
            force (bool): If set to True, the mirror is updated even if the
                          update interval is not yet reached.

        Return:
            Returns True if the mirror was updated or False if the request timed out.
        """
        try:
            with Locker(f"Mirror {self.path}", self.lockfile, self.config):
                if not os.path.exists(self.git_dir):
                    return self._clone(ref)

                if force or self._update_time_reached():
                    return self._update(ref)

                LOG.info("Update time of mirror %s not reached yet.", self.path)
        except portalocker.exceptions.LockException:
            LOG.error("Update timed out due to locked mirror.")
            return False
        return True

    def fetch_lfs(self, ref=None, options=None):
        """Fetch the lfs data of the specified ref for the mirror.

        Args:
            ref (str):      The ref to use for the fetch of the lfs data. If None,
                            the default branch is determined and used.
            options (list): Options of the git lfs fetch call.

        Return:
            Returns True if the lfs fetch was successful.
        """
        if has_git_lfs_cmd():
            try:
                with Locker(f"Mirror {self.path}", self.lockfile, self.config):
                    return self._fetch_lfs(ref, options)
            except portalocker.exceptions.LockException:
                if ref is not None:
                    LOG.error("LFS fetch of %s timed out due to locked mirror.", ref)
                else:
                    LOG.error("LFS fetch of default ref timed out due to locked mirror.")
                return False
            return True

        LOG.warning("LFS fetch skipped as git-lfs is not available on this system!")
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

    @classmethod
    def _rmtree(cls, name, ignore_errors=False):
        """Delete a directory tree.

        Method borrowed from https://github.com/python/cpython/blob/main/Lib/tempfile.py.

        Args:
            cls (class):          The class.
            name (str):           The path to delete.
            ignore_errors (bool): If set to True, ignore errors, otherwise raise them.
        """
        # pylint: disable=unused-argument
        def onerror(func, path, exc_info):
            if issubclass(exc_info[0], PermissionError):
                def resetperms(path):
                    try:
                        os.chflags(path, 0)
                    except AttributeError:
                        pass
                    os.chmod(path, 0o700)

                try:
                    if path != name:
                        resetperms(os.path.dirname(path))
                    resetperms(path)

                    try:
                        os.unlink(path)
                    # PermissionError is raised on FreeBSD for directories
                    except (IsADirectoryError, PermissionError):
                        cls._rmtree(path, ignore_errors=ignore_errors)
                except FileNotFoundError:
                    pass
            elif issubclass(exc_info[0], FileNotFoundError):
                pass
            else:
                if not ignore_errors:
                    # pylint: disable=misplaced-bare-raise
                    raise

        shutil.rmtree(name, onerror=onerror)

    def delete(self):
        """Delete the mirror.

        Return:
            Returns True if the mirror was deleted or False if the request timed out.
        """
        try:
            with Locker(f"Mirror {self.path}", self.lockfile, self.config):
                LOG.debug("Deleting mirror %s", self.path)
                self.database.remove(self.path)
                self._rmtree(self.path, ignore_errors=True)

            # Delete again outside lock to ensure lock file and directory are removed
            if os.path.exists(self.path):
                self._rmtree(self.path, ignore_errors=False)
        except portalocker.exceptions.LockException:
            LOG.error("Delete timed out due to locked mirror.")
            return False
        return True

    def clone_from_mirror(self, git_options):
        """Clone from the mirror.

        Args:
            git_options (obj): The GitOptions object.

        Return:
            Returns the return code of the last command.
        """
        ref = None
        if 'branch' in git_options.command_group_values:
            ref = git_options.command_group_values['branch'][0]

        if not self.update(ref):
            return 1

        git_lfs_url = self.url + "/info/lfs"
        real_git = self.config.get("System", "RealGit")

        new_args = [x if x != self.url else self.git_dir for x in git_options.all_args]
        new_args.insert(0, real_git)
        new_args.insert(1, "-c")
        new_args.insert(2, f"lfs.url={git_lfs_url}")
        if self.config.get('LFS', 'PerMirrorStorage'):
            new_args.insert(3, "-c")
            new_args.insert(4, f"lfs.storage={self.git_lfs_dir}")

        if len(git_options.command_args) > 1:
            target_dir = git_options.command_args[1]
        else:
            target_dir = os.path.basename(self.url).replace('.git', '')
            new_args.append(target_dir)

        return_code, _, _ = pretty_call_command_retry(
            f'Clone from mirror {self.path}',
            '',
            new_args,
            num_retries=self.config.get("Clone", "Retries"),
            command_timeout=self.config.get("Clone", "CommandTimeout"),
            output_timeout=self.config.get("Clone", "OutputTimeout"),
            remove_dir=target_dir)

        if return_code != 0:
            return return_code

        self.database.increment_counter(self.path, "clones")

        LOG.info("Setting push URL to %s and configure LFS.", self.url)
        paths = git_options.get_global_group_values('run_path') + [target_dir]
        cwd = os.path.abspath(os.path.join(*paths))
        commands = [[real_git, "remote", "set-url", "--push", "origin", self.url],
                    [real_git, "config", "--local", "lfs.url", git_lfs_url]]
        if self.config.get('LFS', 'PerMirrorStorage'):
            commands.append([real_git, "config", "--local", "lfs.storage", self.git_lfs_dir])

        retval = 0
        for command in commands:
            cmd_retval = simple_call_command(command, cwd=cwd)
            if cmd_retval != 0:
                LOG.error("Command '%s' with working directory %s gave return code of %d!",
                          command, cwd, cmd_retval)
                retval = cmd_retval
        return retval

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

    def _clone(self, ref=None):
        """Clone the mirror.

        Args:
            ref (str): The ref to use for the fetch of the lfs data. If None,
                       the default branch is determined and used.

        Return:
            Returns True on success.
        """
        command = [self.config.get("System", "RealGit"),
                   'clone', '--progress', '--mirror', self.url, self.git_dir]
        return_code, _, _ = pretty_call_command_retry(
            f'Initial clone of {self.url} into {self.path}',
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

    def _update(self, ref=None, handle_gc_error=True):
        """Update the mirror.

        Args:
            ref (str):              The ref to use for the fetch of the lfs data. If None,
                                    the default branch is determined and used.
            handle_gc_error (bool): If set to True, garbage collection errors are detected
                                    and handled.

        Return:
            Returns True on success.
        """
        command = [self.config.get("System", "RealGit"),
                   'remote', 'update', '--prune']
        return_code, stdout_buffer, stderr_buffer = pretty_call_command_retry(
            f'Update of {self.path}',
            'garbage collection error',
            command,
            num_retries=self.config.get("Update", "Retries"),
            cwd=self.git_dir,
            command_timeout=self.config.get("Update", "CommandTimeout"),
            output_timeout=self.config.get("Update", "OutputTimeout"),
            abort_on_pattern=b'remove gc.log' if handle_gc_error else None)

        if return_code == 0:
            if handle_gc_error:
                if (b'remove gc.log' in stdout_buffer) or (b'remove gc.log' in stderr_buffer):
                    self._run_gc()
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
        command = [self.config.get("System", "RealGit"), 'gc']
        return_code, _, _ = pretty_call_command_retry(
            f'Garbage collection on {self.path}',
            '',
            command,
            num_retries=self.config.get("GC", "Retries"),
            cwd=self.git_dir,
            command_timeout=self.config.get("GC", "CommandTimeout"),
            output_timeout=self.config.get("GC", "OutputTimeout"))

        if return_code == 0:
            gc_log_file = os.path.join(self.git_dir, 'gc.log')
            if os.path.exists(gc_log_file):
                os.unlink(gc_log_file)

        return return_code == 0

    def _fetch_lfs(self, ref=None, options=None):
        """Fetch the lfs data of the specified ref.

        Args:
            ref (str):      The ref to use for the fetch of the lfs data. If None,
                            the default branch is determined and used.
            options (list): Options of the git lfs fetch call.

        Return:
            Returns True if the lfs fetch was successful.
        """
        if not has_git_lfs_cmd():
            LOG.warning("LFS fetch skipped as git-lfs is not available on this system!")
            return True

        git_options = []
        if self.config.get('LFS', 'PerMirrorStorage'):
            git_options = ["-c", f"lfs.storage={self.git_lfs_dir}"]

        if ref is None:
            ref = self.get_default_ref()
            if ref is None:
                LOG.error("Can't determine default ref of git repository!")
                return 1

        command = [self.config.get("System", "RealGit")] + git_options
        command += ["lfs", "fetch"] + (options if options else []) + ["origin", ref]

        return_code, _, _ = pretty_call_command_retry(
            f'LFS fetch of ref {ref} from {self.url} into {self.path}',
            '',
            command,
            num_retries=self.config.get("LFS", "Retries"),
            cwd=self.git_dir,
            command_timeout=self.config.get("LFS", "CommandTimeout"),
            output_timeout=self.config.get("LFS", "OutputTimeout"))

        if return_code == 0:
            self.database.increment_counter(self.path, "lfs-updates")

        return return_code == 0

    def get_default_ref(self):
        """Get the default ref like master or main.

        Return:
            Returns the default ref.
        """
        real_git = self.config.get("System", "RealGit")
        command = [real_git, "symbolic-ref", "--short", "HEAD"]
        return_code, ref = getstatusoutput(command, cwd=self.git_dir)
        if return_code == 0:
            return ref.strip()
        return None

    @staticmethod
    def url_to_path(url):
        """Convert an URL into a repository mirror path.

        Args:
            url (str): The URL of the repository.

        Return:
            Returns the mirror path or None if the url can't be converted.
        """
        if url.startswith('http://') or url.startswith('https://') or url.startswith('ssh://'):
            sub_dir = url.split('//')[1]
            if '@' in sub_dir:
                sub_dir = sub_dir.split('@')[1]
            if ':' in sub_dir:
                sub_dir = sub_dir.replace(':', '_')
            if sub_dir.endswith('.git'):
                sub_dir = sub_dir[:-4]
            if sub_dir.endswith('/'):
                sub_dir = sub_dir[:-1]
            if os.path.sep != '/':
                sub_dir = sub_dir.replace('/', os.path.sep)
            return os.path.join(GITCACHE_DIR, "mirrors", sub_dir)

        # URL is already a path
        if url.startswith(GITCACHE_DIR):
            return url

        return None

    @staticmethod
    def escape_options(options):
        """Convert a list of options into single-quote escaped elements.

        Args:
            options (list): List of options.

        Return:
            Returns a string containing the escaped options separated by
            spaces.
        """
        if options:
            escaped_options = [f"'{option}'" for option in options]
            return ' '.join(escaped_options)

        return ''

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
