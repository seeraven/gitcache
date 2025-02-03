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
import posixpath
import re
from typing import List, Optional

import portalocker

from .command_execution import getstatusoutput, pretty_call_command_retry, simple_call_command
from .config import Config, has_git_lfs_cmd
from .database import Database
from .git_options import GitOptions
from .global_settings import GITCACHE_DIR
from .helpers import rmtree

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Regular Expressions
# -----------------------------------------------------------------------------

# Pattern to match ssh, git, http[s] and ftp[s]:
#                                  <proto>      [user@]  <host>  [:port]   <path>
RE_URL_WITH_PROTO = re.compile(r"([a-zA-Z]+)://([^@]+@)?([^:/]+)(:[0-9]+)?/(.*)")

# Pattern to match scp-like syntax:  [user@]  <host>       <path>
RE_URL_WITHOUT_PROTO = re.compile(r"([^@]+@)?([^:/\\]{2,}):(.*)")

# Pattern to match file://<path>
RE_URL_WITH_FILE = re.compile(r"file://(.*)")


# -----------------------------------------------------------------------------
# Class Definitions
# -----------------------------------------------------------------------------
class Locker:
    """A lock for the mirror."""

    def __init__(self, name, filename, config, ensure_dir=True):
        """Construct a new lock object for the mirror.

        Args:
            name (str):       The name of the item that is locked.
            filename (str):   The lock file.
            config (obj):     The config.Config object to get the settings.
            ensure_dir(bool): Create the path to filename if not yet existed.
        """
        self.name = name
        if ensure_dir:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
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


# pylint: disable=too-many-instance-attributes
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

        if self.url:
            self.normalized_url = self.normalize_url(url)

        if self.url and self.path is None:
            self.path = self.get_mirror_path(self.url)

        if self.path and self.url is None:
            self.url = self.database.get_url_for_path(self.path)
        self.lockfile = os.path.join(os.path.dirname(self.path), ".lock", os.path.basename(self.path))

        self.git_dir = os.path.join(self.path, "git")
        self.git_lfs_dir = os.path.join(self.path, "lfs")
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
        mirror_exists = self.database.get(self.path) is not None
        try:
            with Locker(f"Mirror {self.path}", self.lockfile, self.config):
                if not mirror_exists:
                    rmtree(self.path, ignore_errors=True)
                    return self._clone(ref)

                if force or self._update_time_reached():
                    return self._update(ref)

                LOG.info("Update time of mirror %s not reached yet.", self.path)
        except portalocker.exceptions.LockException:
            LOG.error("Update timed out due to locked mirror.")
            return False
        return True

    def fetch(self, command_args: List[str]) -> bool:
        """Execute a fetch command with custom arguments in the mirror.

        Args:
            command_args (list): A list of strings giving additional arguments
                                 to the fetch command executed in the mirror.

        Return:
            Returns True if the command was successfull, otherwise False.
        """
        mirror_exists = self.database.get(self.path) is not None
        try:
            with Locker(f"Mirror {self.path}", self.lockfile, self.config):
                if not mirror_exists:
                    LOG.error("Mirror does not exist!")
                    return False
                return self._fetch(command_args)
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

    def delete(self):
        """Delete the mirror.

        Return:
            Returns True if the mirror was deleted or False if the request timed out.
        """
        try:
            with Locker(f"Mirror {self.path}", self.lockfile, self.config):
                LOG.debug("Deleting mirror %s", self.path)
                self.database.remove(self.path)
                rmtree(self.path, ignore_errors=True)

            # Delete again outside lock to ensure lock file and directory are removed
            if os.path.exists(self.path):
                rmtree(self.path, ignore_errors=False)
        except portalocker.exceptions.LockException:
            LOG.error("Delete timed out due to locked mirror.")
            return False
        return True

    def clone_from_mirror(self, git_options: GitOptions) -> int:
        """Clone from the mirror.

        Args:
            git_options (obj): The GitOptions object.

        Return:
            Returns the return code of the last command.
        """
        ref = None
        if "branch" in git_options.command_group_values:
            ref = git_options.command_group_values["branch"][0]

        if not self.update(ref):
            return 1

        git_lfs_url = self.url + "/info/lfs"
        real_git = self.config.get("System", "RealGit")

        new_args = [x if x != self.url else self.git_dir for x in git_options.all_args]
        for option in ["--recursive", "--recurse-submodules", "--remote-submodules"]:
            if option in new_args:
                new_args.remove(option)
        new_args.insert(0, real_git)
        new_args.insert(1, "-c")
        new_args.insert(2, f"lfs.url={git_lfs_url}")
        if self.config.get("LFS", "PerMirrorStorage"):
            new_args.insert(3, "-c")
            new_args.insert(4, f"lfs.storage={self.git_lfs_dir}")

        if len(git_options.command_args) > 1:
            target_dir = git_options.command_args[1]
        else:
            target_dir = os.path.basename(self.url).replace(".git", "")
            new_args.append(target_dir)

        return_code, _, _ = pretty_call_command_retry(
            f"Clone from mirror {self.path}",
            "",
            new_args,
            num_retries=self.config.get("Clone", "Retries"),
            command_timeout=self.config.get("Clone", "CommandTimeout"),
            output_timeout=self.config.get("Clone", "OutputTimeout"),
            remove_dir=target_dir,
        )

        if return_code != 0:
            return return_code

        self.database.increment_counter(self.path, "clones")

        LOG.info("Setting push URL to %s and configure LFS.", self.url)
        paths = [path for path in git_options.get_global_group_values("run_path") if path is not None] + [target_dir]
        cwd = os.path.abspath(os.path.join(*paths))
        commands = [
            [real_git, "remote", "set-url", "--push", "origin", self.url],
            [real_git, "config", "--local", "lfs.url", git_lfs_url],
        ]
        if self.config.get("LFS", "PerMirrorStorage"):
            commands.append([real_git, "config", "--local", "lfs.storage", self.git_lfs_dir])

        retval = 0
        for command in commands:
            cmd_retval = simple_call_command(command, cwd=cwd)
            if cmd_retval != 0:
                LOG.error("Command '%s' with working directory %s gave return code of %d!", command, cwd, cmd_retval)
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
        return self.database.get_time_since_last_update(self.path) >= self.config.get("MirrorHandling", "CleanupAfter")

    def _clone(self, ref=None):
        """Clone the mirror.

        Args:
            ref (str): The ref to use for the fetch of the lfs data. If None,
                       the default branch is determined and used.

        Return:
            Returns True on success.
        """
        if self.config.get("Clone", "CloneStyle").lower() == "partialfirst":
            command = [self.config.get("System", "RealGit"), "clone", "--progress", "--depth=1", self.url, self.git_dir]
            return_code, _, _ = pretty_call_command_retry(
                f"Partial clone of {self.url} into {self.path}",
                "",
                command,
                num_retries=self.config.get("Clone", "Retries"),
                command_timeout=self.config.get("Clone", "CommandTimeout"),
                output_timeout=self.config.get("Clone", "OutputTimeout"),
                remove_dir=self.git_dir,
            )
            if return_code != 0:
                return False

            command = [self.config.get("System", "RealGit"), "-C", self.git_dir, "fetch", "--unshallow"]
            return_code, _, _ = pretty_call_command_retry(
                f"Fetching the rest of {self.url} into {self.path}",
                "",
                command,
                num_retries=self.config.get("Clone", "Retries"),
                command_timeout=self.config.get("Clone", "CommandTimeout"),
                output_timeout=self.config.get("Clone", "OutputTimeout"),
                # remove_dir=self.git_dir,
            )
            if return_code != 0:
                rmtree(self.git_dir, ignore_errors=True)

        else:
            command = [self.config.get("System", "RealGit"), "clone", "--progress", "--mirror", self.url, self.git_dir]

            return_code, _, _ = pretty_call_command_retry(
                f"Initial clone of {self.url} into {self.path}",
                "",
                command,
                num_retries=self.config.get("Clone", "Retries"),
                command_timeout=self.config.get("Clone", "CommandTimeout"),
                output_timeout=self.config.get("Clone", "OutputTimeout"),
                remove_dir=self.git_dir,
            )

        if return_code == 0:
            self.database.add(self.normalized_url, self.path)
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
        command = [self.config.get("System", "RealGit"), "remote", "update", "--prune"]
        return_code, stdout_buffer, stderr_buffer = pretty_call_command_retry(
            f"Update of {self.path}",
            "garbage collection error",
            command,
            num_retries=self.config.get("Update", "Retries"),
            cwd=self.git_dir,
            command_timeout=self.config.get("Update", "CommandTimeout"),
            output_timeout=self.config.get("Update", "OutputTimeout"),
            abort_on_pattern=b"remove gc.log" if handle_gc_error else None,
        )

        if return_code == 0:
            if handle_gc_error:
                if (b"remove gc.log" in stdout_buffer) or (b"remove gc.log" in stderr_buffer):
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
        command = [self.config.get("System", "RealGit"), "gc"]
        return_code, _, _ = pretty_call_command_retry(
            f"Garbage collection on {self.path}",
            "",
            command,
            num_retries=self.config.get("GC", "Retries"),
            cwd=self.git_dir,
            command_timeout=self.config.get("GC", "CommandTimeout"),
            output_timeout=self.config.get("GC", "OutputTimeout"),
        )

        if return_code == 0:
            gc_log_file = os.path.join(self.git_dir, "gc.log")
            if os.path.exists(gc_log_file):
                os.unlink(gc_log_file)

        return return_code == 0

    def _fetch(self, command_args: List[str]) -> bool:
        """Execute a fetch command with custom arguments in the mirror.

        Args:
            command_args (list): A list of strings giving additional arguments
                                 to the fetch command executed in the mirror.

        Return:
            Returns True if the command was successfull, otherwise False.
        """
        command = [self.config.get("System", "RealGit"), "fetch"] + command_args
        return_code, _, _ = pretty_call_command_retry(
            f"Explicit fetch on {self.path} with arguments {command_args}",
            "",
            command,
            num_retries=self.config.get("Update", "Retries"),
            cwd=self.git_dir,
            command_timeout=self.config.get("Update", "CommandTimeout"),
            output_timeout=self.config.get("Update", "OutputTimeout"),
        )
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
        if self.config.get("LFS", "PerMirrorStorage"):
            git_options = ["-c", f"lfs.storage={self.git_lfs_dir}"]

        if ref is None:
            ref = self.get_default_ref()
            if ref is None:
                LOG.error("Can't determine default ref of git repository!")
                return 1

        command = [self.config.get("System", "RealGit")] + git_options
        command += ["lfs", "fetch"] + (options if options else []) + ["origin", ref]

        return_code, _, _ = pretty_call_command_retry(
            f"LFS fetch of ref {ref} from {self.url} into {self.path}",
            "",
            command,
            num_retries=self.config.get("LFS", "Retries"),
            cwd=self.git_dir,
            command_timeout=self.config.get("LFS", "CommandTimeout"),
            output_timeout=self.config.get("LFS", "OutputTimeout"),
        )

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
    def normalize_url(url: str) -> str:
        """Normalize the given URL.

        Args:
            url (str): The URL of the repository.

        Return:
            Returns the normalized URL.
        """
        # file:// urls are not mirrored
        if match := RE_URL_WITH_FILE.match(url):
            return url

        if match := RE_URL_WITH_PROTO.match(url):
            path = posixpath.normpath(match.group(5))
            while path.startswith("../"):
                path = path[3:]
            while path.endswith("/"):
                path = path[:-1]
            if path.endswith(".git"):
                path = path[:-4]
            return f"{match.group(1)}://{match.group(2) or ''}{match.group(3)}{match.group(4) or ''}/{path}"

        if match := RE_URL_WITHOUT_PROTO.match(url):
            path = posixpath.normpath(match.group(3))
            while path.startswith("../"):
                path = path[3:]
            while path.endswith("/"):
                path = path[:-1]
            if path.endswith(".git"):
                path = path[:-4]
            return f"{match.group(1) or ''}{match.group(2)}:{path}"

        return url

    @staticmethod
    # pylint: disable=too-many-branches,too-many-return-statements
    def get_mirror_path(url) -> Optional[str]:
        """Convert an URL into a repository mirror path.

        Args:
            url (str): The URL of the repository.

        Return:
            Returns the full path to the mirror directory. If the
            given URL is a local path (which is not mirrored) or
            can not be parsed, None is returned.
        """
        sub_dir = None
        if match := RE_URL_WITH_FILE.match(url):
            return None

        if match := RE_URL_WITH_PROTO.match(url):
            sub_dir = match.group(3)
            port = match.group(4)
            if port is not None:
                sub_dir += port.replace(":", "_")
            path = posixpath.normpath(match.group(5))
            while path.startswith("../"):
                path = path[3:]
            sub_dir += "/" + posixpath.normpath(path)

        elif match := RE_URL_WITHOUT_PROTO.match(url):
            path = posixpath.normpath(match.group(3))
            while path.startswith("../"):
                path = path[3:]
            sub_dir = match.group(2) + "/" + path

        else:
            return None

        sub_dir = sub_dir.replace("//", "/")
        while sub_dir.startswith("/"):
            sub_dir = sub_dir[1:]
        while sub_dir.endswith("/"):
            sub_dir = sub_dir[:-1]
        if sub_dir.endswith(".git"):
            sub_dir = sub_dir[:-4]
        if os.path.sep != "/":
            sub_dir = sub_dir.replace("/", os.path.sep)
        return os.path.join(GITCACHE_DIR, "mirrors", sub_dir)

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
            return " ".join(escaped_options)

        return ""


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
