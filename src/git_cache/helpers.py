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
import shutil

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
