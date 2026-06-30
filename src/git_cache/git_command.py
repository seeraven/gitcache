# -*- coding: utf-8 -*-
"""
Handler for the git command wrapper.

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
import sys
from typing import List

from .command_execution import simple_call_command
from .commands.checkout import git_checkout
from .commands.cleanup import git_cleanup
from .commands.clone import git_clone
from .commands.delete import git_delete_mirror
from .commands.fetch import git_fetch
from .commands.lfs_fetch import git_lfs_fetch
from .commands.lfs_pull import git_lfs_pull
from .commands.ls_remote import git_ls_remote
from .commands.pull import git_pull
from .commands.remote_add import git_remote_add
from .commands.submodule_init import git_submodule_init
from .commands.submodule_update import git_submodule_update
from .commands.update_all import git_update_all_mirrors
from .config import Config
from .git_options import GitOptions
from .invocation_log import set_mode_disabled, set_mode_gitcache, set_mode_realgit

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def is_gitcache_disabled() -> bool:
    """Return whether gitcache command wrapping is disabled.

    The setting can be configured via :code:`System/Disable` in the configuration
    file or the environment variable :code:`GITCACHE_DISABLE`. Values
    :code:`1`, :code:`true`, :code:`yes` and :code:`on` (case-insensitive) enable
    this behavior.
    """
    config = Config()
    return config.get("System", "Disable")


def call_real_git(args: List[str]) -> int:
    """Call the real git command with the given arguments.

    Args:
        args (list):          The arguments to git.

    Return:
        Returns the return code of the call.
    """
    config = Config()
    return simple_call_command([config.get("System", "RealGit")] + args)


# pylint: disable=too-many-branches,too-many-statements
def handle_git_command(called_as: List[str], args: List[str]) -> None:
    """Handle a git command.

    Args:
        called_as (list): The arguments used for the command call.
        args (list):      The arguments to git.
    """
    LOG.debug("handle_git_command(%s, %s) started", called_as, args)

    if is_gitcache_disabled():
        LOG.debug("gitcache disabled by configuration. Calling real git command.")
        set_mode_disabled()
        sys.exit(call_real_git(args))

    git_options = GitOptions(args)
    if git_options.has_bail_out():
        LOG.debug("bail out")
        set_mode_realgit("bail_out")
        sys.exit(call_real_git(args))

    LOG.debug(
        "Found global options %s, command '%s', command options '%s' and arguments %s.",
        git_options.global_options,
        git_options.get_command(),
        git_options.command_options,
        git_options.command_args,
    )

    command = git_options.get_command()
    if command == "cleanup":
        set_mode_gitcache(command)
        sys.exit(git_cleanup())

    elif command == "update-mirrors":
        set_mode_gitcache(command)
        sys.exit(git_update_all_mirrors())

    elif command == "delete-mirror":
        set_mode_gitcache(command)
        sys.exit(git_delete_mirror(git_options.command_args))

    elif command == "ls-remote":
        set_mode_gitcache(command)
        sys.exit(git_ls_remote(git_options))

    elif command == "checkout":
        set_mode_gitcache(command)
        sys.exit(git_checkout(git_options))

    elif command == "clone":
        set_mode_gitcache(command)
        sys.exit(git_clone(called_as, git_options))

    elif command == "lfs_fetch":
        set_mode_gitcache(command)
        sys.exit(git_lfs_fetch(git_options))

    elif command == "lfs_pull":
        set_mode_gitcache(command)
        sys.exit(git_lfs_pull(git_options))

    elif command == "pull":
        set_mode_gitcache(command)
        sys.exit(git_pull(git_options))

    elif command == "fetch":
        set_mode_gitcache(command)
        sys.exit(git_fetch(git_options))

    elif command == "submodule_init":
        set_mode_gitcache(command)
        sys.exit(git_submodule_init(git_options))

    elif command == "submodule_update":
        set_mode_gitcache(command)
        sys.exit(git_submodule_update(called_as, git_options))

    elif command == "remote_add":
        set_mode_gitcache(command)
        sys.exit(git_remote_add(git_options))

    LOG.debug("Command '%s' is not handled by gitcache. Calling the real git command.", git_options.get_command())
    set_mode_realgit("unhandled_command")
    sys.exit(call_real_git(args))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
