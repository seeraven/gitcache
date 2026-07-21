"""
Helper functions for gitcache

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
import re
import shutil
from typing import Optional

# Pattern to match ssh, git, http[s] and ftp[s]:
#                                  <proto>      [user@]  <host>  [:port]   <path>
_RE_URL_WITH_PROTO = re.compile(r"([a-zA-Z]+)://([^@]+@)?([^:/]+)(:[0-9]+)?/(.*)")

# Pattern to match scp-like syntax:  [user@]  <host>       <path>
_RE_URL_WITHOUT_PROTO = re.compile(r"([^@]+@)?([^:/\\]{2,}):(.*)")

# Pattern to match file://<path>
_RE_URL_WITH_FILE = re.compile(r"file://(.*)")

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


def rmtree(name: str, ignore_errors: bool = False, repeated: bool = False) -> None:
    """Delete a directory tree.

    Method borrowed from https://github.com/python/cpython/blob/main/Lib/tempfile.py.

    Args:
        name (str):           The path to delete.
        ignore_errors (bool): If set to True, ignore errors, otherwise raise them.
        repeated (bool):      Internal used flag to indicate a repeated call.
    """
    LOG.debug("Deleting directory tree %s", name)

    # pylint: disable=unused-argument
    def onerror(func, path, exc_info):
        if issubclass(exc_info[0], PermissionError):
            if repeated and (path == name):
                LOG.warning("Persistent error trying to delete %s!", path)
                if ignore_errors:
                    return
                # pylint: disable=misplaced-bare-raise
                raise

            def dont_follow_symlinks(func, path, *args):
                if func in os.supports_follow_symlinks:
                    func(path, *args, follow_symlinks=False)
                elif not os.path.islink(path):
                    func(path, *args)

            def resetperms(path):
                try:
                    chflags = os.chflags
                except AttributeError:
                    pass
                else:
                    dont_follow_symlinks(chflags, path, 0)
                dont_follow_symlinks(os.chmod, path, 0o700)

            try:
                LOG.debug(
                    "Permission error while deleting %s. Trying to reset permissions of that file/directory.", path
                )
                if path != name:
                    resetperms(os.path.dirname(path))
                resetperms(path)

                try:
                    os.unlink(path)
                    LOG.debug("File %s deleted successfully after resetting the permissions.", path)
                except IsADirectoryError:
                    rmtree(path, ignore_errors=ignore_errors)
                except PermissionError:
                    # The PermissionError handler was originally added for
                    # FreeBSD in directories, but it seems that it is raised
                    # on Windows too.
                    # bpo-43153: Calling _rmtree again may
                    # raise NotADirectoryError and mask the PermissionError.
                    # So we must re-raise the current PermissionError if
                    # path is not a directory.

                    # Note, for Python 3.12+ we would need
                    #   if not os.path.isdir(path) or os.path.isjunction(path):
                    # but older python versions do not have the isjunction()
                    # function!
                    if not os.path.isdir(path):
                        LOG.warning("Unable to delete file %s even after resetting the permissions.", path)
                        if ignore_errors:
                            return
                        raise
                    same_path = path == name
                    rmtree(path, ignore_errors=ignore_errors, repeated=same_path)
            except FileNotFoundError:
                pass
        elif issubclass(exc_info[0], FileNotFoundError):
            pass
        else:
            if not ignore_errors:
                # pylint: disable=misplaced-bare-raise
                raise
            LOG.debug("Ignoring exception %s during rmtree.", exc_info[0])

    # On newer python versions the onerror argument is deprecated:
    # pylint: disable=deprecated-argument
    shutil.rmtree(name, onerror=onerror)


def keep_username(creds: Optional[str]) -> str:
    """Reduce a credentials part of an URL to the plain 'user@' prefix.

    Args:
        creds (str): The credentials part of an URL including the trailing '@',
                     e.g. 'user@' or 'user:password@'. May be None or empty.

    Return:
        Returns the 'user@' prefix without any password, or an empty string
        if no credentials were given.
    """
    if not creds:
        return ""
    return creds[:-1].split(":", 1)[0] + "@"


def _strip_password(creds: str, mask: bool = False) -> str:
    """Remove the password from a credentials part of an SSH URL.

    The username is required for SSH authentication and therefore kept.

    Args:
        creds (str): The credentials part of an URL including the trailing '@',
                     e.g. 'user@' or 'user:password@'.
        mask (bool): If set to True the password is replaced with [MASKED].

    Return:
        Returns 'user@' resp. 'user:[MASKED]@' if masking a password.
    """
    has_password = ":" in creds[:-1]
    if has_password and mask:
        return keep_username(creds)[:-1] + ":[MASKED]@"
    return keep_username(creds)


def strip_credentials(url: str, mask: bool = False) -> str:
    """Remove any credentials from the specified url.

    Args:
        url (str):   The URL of the repository.
        mask (bool): If set to True the removed parts are replaced with [MASKED].

    Return:
        Returns the URL without credentials.
    """
    if match := _RE_URL_WITH_FILE.match(url):
        return url

    if match := _RE_URL_WITH_PROTO.match(url):
        proto, creds, host, port, path = match.groups()
        if not creds:
            return url
        if proto.lower() == "ssh":
            return f"{proto}://{_strip_password(creds, mask)}{host}{port or ''}/{path}"
        return f"{proto}://{'[MASKED]@' if mask else ''}{host}{port or ''}/{path}"

    if match := _RE_URL_WITHOUT_PROTO.match(url):
        # For SCP-style URLs (user@host:path), keep the username as-is. SCP syntax
        # has no place for a password, so there is nothing to strip or mask here.
        return url

    return url


def subprocess_env() -> dict:
    """Return a copy of the environment safe for RealGit child processes.

    Strips invocation log settings so nested ``git`` calls via PATH (e.g. from
    git-lfs) do not write into the parent's log files.
    """
    env = os.environ.copy()
    for key in ("GITCACHE_DETAIL_LOG", "GITCACHE_SUMMARY_LOG", "GITCACHE_DETAIL_LOG_LEVEL"):
        env.pop(key, None)
    return env
