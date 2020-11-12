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

from .command_execution import simple_call_command
from .commands.checkout import git_checkout
from .commands.cleanup import git_cleanup
from .commands.clone import git_clone
from .commands.delete import git_delete_mirror
from .commands.fetch import git_fetch
from .commands.lfs_fetch import git_lfs_fetch
from .commands.ls_remote import git_ls_remote
from .commands.pull import git_pull
from .commands.submodule_init import git_submodule_init
from .commands.submodule_update import git_submodule_update
from .commands.update_all import git_update_all_mirrors
from .config import Config


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def split_git_command(args):
    """Split the git command into global options of interest, command and command arguments.

    Args:
        args (list): The arguments to git.

    Return:
        Returns the tuple (global_options, command, arguments).
    """
    ignore_options_with_argument = ['--namespace', '--super-prefix']
    append_options_with_argument = ['-C', '-c', '--git-dir', '--work-tree']
    append_options_starting_with = ['--git-dir=', '--work-tree=']

    global_options = []
    command = None
    arguments = []

    append_next = False
    ignore_next = False

    for arg in args:
        if command is None:
            if append_next:
                global_options.append(arg)
                append_next = False
            elif ignore_next:
                ignore_next = False
            elif arg in ignore_options_with_argument:
                ignore_next = True
            elif arg in append_options_with_argument:
                global_options.append(arg)
                append_next = True
            elif any(arg.startswith(x) for x in append_options_starting_with):
                global_options.append(arg)
            elif not arg.startswith('-'):
                command = arg
        else:
            arguments.append(arg)

    return (global_options, command, arguments)


def call_real_git(args):
    """Call the real git command with the given arguments.

    Args:
        args (list):          The arguments to git.

    Return:
        Returns the return code of the call.
    """
    config = Config()
    return simple_call_command([config.get("System", "RealGit")] + args)


def handle_git_command(called_as, args):
    """Handle a git command.

    Args:
        called_as (list): The arguments used for the command call.
        args (list):      The arguments to git.
    """
    LOG.debug("handle_git_command(%s, %s) started", called_as, args)

    bail_out_options = ['--help', '-h', '--version',
                        '--exec-path', '--html-path', '--man-path', '--info-path']
    if not args or any(x in bail_out_options for x in args):
        LOG.debug("bail out")
        sys.exit(call_real_git(args))

    global_options, command, command_arguments = split_git_command(args)
    LOG.debug("Found global options %s, command '%s' and arguments %s.",
              global_options, command, command_arguments)

    if command == "cleanup":
        sys.exit(git_cleanup())

    elif command == "update-mirrors":
        sys.exit(git_update_all_mirrors())

    elif command == 'delete-mirror':
        sys.exit(git_delete_mirror(command_arguments))

    elif command == 'ls-remote':
        sys.exit(git_ls_remote(args, global_options, command_arguments))

    elif command == 'checkout':
        sys.exit(git_checkout(args, global_options, command_arguments))

    elif command == 'clone':
        sys.exit(git_clone(args, command_arguments))

    elif command == 'lfs' and 'fetch' in command_arguments:
        sys.exit(git_lfs_fetch(args, global_options, command_arguments))

    elif command == 'pull':
        sys.exit(git_pull(args, global_options))

    elif command == 'fetch':
        sys.exit(git_fetch(args, global_options, command_arguments))

    elif command == 'submodule' and 'init' in command_arguments:
        sys.exit(git_submodule_init(args, global_options))

    elif command == 'submodule' and 'update' in command_arguments:
        sys.exit(git_submodule_update(called_as, args, global_options, command_arguments[1:]))

    LOG.debug("Command '%s' is not handled by gitcache. Calling the real git command.", command)
    sys.exit(call_real_git(args))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
