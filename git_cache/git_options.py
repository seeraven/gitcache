# -*- coding: utf-8 -*-
"""
Option parser for git commands.

Copyright:
    2021 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging

from .config import Config


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Option Definitions
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class Option:
    """Definition of a git command option."""

    # pylint: disable=too-many-arguments
    def __init__(self, group='ignored', short_name=None, long_name=None, has_arg=True,
                 has_stuck=True, has_separate=True):
        """Construct a new option.

        Args:
            group (str):         Name of a group used to access the option.
            short_name (str):    Short option name, e.g., 'p' for option '-p'.
            long_name (str):     Long option name, e.g., 'prune' for option '--prune'.
            has_arg (bool):      Distinguish between boolean options and options with
                                 an argument.
            has_stuck (bool):    Supports the stuck format, e.g., '-oArg' or '--option=Arg'.
            has_separate (bool): Supports the separate format, e.g., '-o Arg' or '--option Arg'.
        """
        self.group = group
        self.short_name = short_name
        self.long_name = long_name
        self.has_arg = has_arg
        self.has_stuck = has_stuck
        self.has_separate = has_separate

        self._options = []
        if self.has_separate:
            if self.short_name:
                self._options.append(f"-{self.short_name}")
            if self.long_name:
                self._options.append(f"--{self.long_name}")

        self._option_prefixes = []
        if self.has_arg and self.has_stuck:
            if self.short_name:
                self._option_prefixes.append(f"-{self.short_name}")
            if self.long_name:
                self._option_prefixes.append(f"--{self.long_name}=")

    def parse(self, args):
        """Try to parse this option from the given arguments.

        Args:
            args (list): The argument list starting with this option.

        Return:
            Returns the tuple (matches, consumed, value) if the given arguments
            match this option. 'matches' is a boolean flag indicating whether
            the option was found. 'consumed' gives the number of arguments
            consumed to parse this option. 'value' gives the extracted value
            or None if the value was not found or the option has no value.
        """
        for option in self._options:
            if args[0] == option:
                if self.has_arg and len(args) > 1:
                    return (True, 2, args[1])
                return (True, 1, None)

        for option_prefix in self._option_prefixes:
            if args[0].startswith(option_prefix):
                return (True, 1, args[0][len(option_prefix):])

        return (False, 0, None)


# Global options (see 'man git' or https://github.com/git/git/blob/master/git.c)
# Please note that the global options are not handled consistently by git. Here,
# only options with arguments and boolean options of interest are listed here.
#
# The group identifies the various scenarios we have:
#  bail_out    If any of these options is given, we can stop parsing right away
#              and call the real git command.
#  run_path    Required to reconstruct the target path for 'git clone' commands.
#
GLOBAL_OPTIONS = [Option(group='bail_out', short_name='h', long_name='help', has_arg=False),
                  Option(group='bail_out', long_name='version',              has_arg=False),
                  Option(group='bail_out', long_name='exec-path',            has_arg=False),
                  Option(group='bail_out', long_name='html-path',            has_arg=False),
                  Option(group='bail_out', long_name='man-path',             has_arg=False),
                  Option(group='bail_out', long_name='info-path',            has_arg=False),
                  Option(group='run_path', short_name='C',                   has_stuck=False),
                  Option(short_name='c',           has_stuck=False),
                  Option(long_name='exec-path',    has_separate=False),
                  Option(long_name='git-dir'),
                  Option(long_name='namespace'),
                  Option(long_name='work-tree'),
                  Option(long_name='super-prefix'),
                  Option(long_name='config-env'),
                  Option(long_name='shallow-file', has_stuck=False),
                  Option(group='bail_out',     long_name='list-cmds',    has_separate=False)]

# ls-remote options taken from https://github.com/git/git/blob/master/builtin/ls-remote.c
# Only options with arguments and boolean options of interest are listed here.
# (Look for OPT_STRING, OPT_INTEGER, OPT_CALLBACK_F, OPT_STRING_LIST)
LS_REMOTE_OPTIONS = [Option(long_name='upload-pack'),
                     Option(long_name='exec'),
                     Option(long_name='sort'),
                     Option(short_name='o', long_name='server-option')]

# checkout options taken from https://github.com/git/git/blob/master/builtin/checkout.c
# Only options with arguments and boolean options of interest are listed here.
# (Look for OPT_STRING, OPT_INTEGER, OPT_CALLBACK_F, OPT_STRING_LIST)
CHECKOUT_OPTIONS = [Option(short_name='b'),
                    Option(short_name='B'),
                    Option(long_name='recurse-submodules'),
                    Option(long_name='conflict'),
                    Option(long_name='orphan'),
                    Option(long_name='pathspec-from-file')]

# clone options taken from https://github.com/git/git/blob/master/builtin/clone.c
# Only options with arguments and boolean options of interest are listed here.
# (Look for OPT_STRING, OPT_INTEGER, OPT_CALLBACK_F, OPT_STRING_LIST)
CLONE_OPTIONS = [Option(long_name='recurse-submodules'),
                 Option(long_name='recursive'),
                 Option(short_name='j', long_name='jobs'),
                 Option(long_name='template'),
                 Option(long_name='reference'),
                 Option(long_name='reference-if-able'),
                 Option(short_name='o', long_name='origin'),
                 Option(group='branch', short_name='b', long_name='branch'),
                 Option(short_name='u', long_name='upload-pack'),
                 Option(long_name='depth'),
                 Option(long_name='shallow-since'),
                 Option(long_name='shallow-exclude'),
                 Option(long_name='separate-git-dir'),
                 Option(short_name='c', long_name='config'),
                 Option(long_name='server-option'),
                 Option(long_name='filter')]

# LFS fetch options taken from
# https://github.com/git-lfs/git-lfs/blob/main/commands/command_fetch.go
# Only options with arguments and boolean options of interest are listed here.
LFS_FETCH_OPTIONS = [Option(short_name='I', long_name='include'),
                     Option(short_name='X', long_name='exclude'),
                     Option(short_name='r', long_name='recent', has_arg=False),
                     Option(short_name='a', long_name='all',    has_arg=False),
                     Option(short_name='p', long_name='prune',  has_arg=False)]

# Pull options taken from https://github.com/git/git/blob/master/builtin/pull.c
# Only options with arguments and boolean options of interest are listed here.
# (Look for OPT_STRING, OPT_INTEGER, OPT_CALLBACK_F, OPT_STRING_LIST)
PULL_OPTIONS = [Option(long_name='recurse-submodules'),
                Option(short_name='r', long_name='rebase'),
                Option(long_name='log'),
                Option(long_name='cleanup'),
                Option(short_name='s', long_name='strategy'),
                Option(short_name='X', long_name='strategy-option'),
                Option(short_name='S', long_name='gpg-sign'),
                Option(long_name='upload-pack'),
                Option(short_name='j', long_name='jobs'),
                Option(long_name='depth'),
                Option(long_name='shallow-since'),
                Option(long_name='shallow-exclude'),
                Option(long_name='deepen'),
                Option(long_name='refmap'),
                Option(short_name='o', long_name='server-option'),
                Option(long_name='negotiation-tip')]

# Fetch options taken from https://github.com/git/git/blob/master/builtin/fetch.c
# Only options with arguments and boolean options of interest are listed here.
# (Look for OPT_STRING, OPT_INTEGER, OPT_CALLBACK_F, OPT_STRING_LIST)
FETCH_OPTIONS = [Option(long_name='upload-pack'),
                 Option(short_name='j', long_name='jobs'),
                 Option(long_name='recurse-submodules'),
                 Option(long_name='depth'),
                 Option(long_name='shallow-since'),
                 Option(long_name='shallow-exclude'),
                 Option(long_name='deepen'),
                 Option(long_name='submodule-prefix'),
                 Option(long_name='recurse-submodules-default'),
                 Option(long_name='refmap'),
                 Option(short_name='o', long_name='server-option'),
                 Option(long_name='negotiation-tip'),
                 Option(long_name='filter')]

# Submodule init options taken from https://github.com/git/git/blob/master/git-submodule.sh
# Only options with arguments and boolean options of interest are listed here.
SUBMODULE_INIT_OPTIONS = []

# Submodule update options taken from https://github.com/git/git/blob/master/git-submodule.sh
# Only options with arguments and boolean options of interest are listed here.
SUBMODULE_UPDATE_OPTIONS = [Option(group='init', long_name='init', has_arg=False),
                            Option(long_name='reference'),
                            Option(long_name='depth'),
                            Option(short_name='j', long_name='jobs')]

COMMAND_OPTIONS = {'lfs':              [],   # Options between 'lfs' and the subcommand
                   'submodule':        [],   # Options between 'submodule' and the subcommand
                   'cleanup':          [],
                   'update-mirrors':   [],
                   'delete-mirror':    [],
                   'ls-remote':        LS_REMOTE_OPTIONS,
                   'checkout':         CHECKOUT_OPTIONS,
                   'clone':            CLONE_OPTIONS,
                   'lfs_fetch':        LFS_FETCH_OPTIONS,
                   'pull':             PULL_OPTIONS,
                   'fetch':            FETCH_OPTIONS,
                   'submodule_init':   SUBMODULE_INIT_OPTIONS,
                   'submodule_update': SUBMODULE_UPDATE_OPTIONS}


# -----------------------------------------------------------------------------
# Main Parser Class
# -----------------------------------------------------------------------------
class GitOptions:
    """Main parser class for the git command line."""

    def __init__(self, args):
        """Construct a GitOptions object from the given arguments.

        Args:
            args (list): The arguments to git without the actual git command.
        """
        self.all_args = args            # All arguments
        self.global_options = []        # All global options
        self.global_group_values = {}   # Map of group to list of (option) values
        self.command = None             # The command
        self.command_options = []       # The command options
        self.command_args = []          # The command arguments
        self.command_group_values = {}  # Map of group to list of (option) values
        self._parse(args)

    def has_bail_out(self):
        """Check if a bail out option was given.

        A bail out option is an option that would cause the real git command
        to exit without performing any subcommand.

        Return:
            Returns True if a bail out option was given.
        """
        return 'bail_out' in self.global_group_values

    def get_command(self):
        """Get the command.

        Return:
            Returns the command like 'fetch' or 'lfs_fetch'.
        """
        return self.command

    def get_real_git_with_options(self):
        """Get a command string consisting of the real git command and all global options.

        Return:
            Returns a command string consisting of the real git command and
            all global options.
        """
        config = Config()
        real_git = config.get("System", "RealGit")
        global_options_str = ' '.join([f"'{i}'" for i in self.global_options])
        return f"{real_git} {global_options_str}"

    def get_real_git_all_args(self):
        """Get a list of command line arguments to call the real git command.

        Return:
            Returns a list of command line arguments to call the real git
            command with all the arguments given to the wrapper.
        """
        config = Config()
        real_git = config.get("System", "RealGit")
        return [real_git] + self.all_args

    def get_run_path_cd_commands(self):
        """Get a command string performing 'cd' commands matching the '-C' global options.

        Return:
            Returns a command string performing all 'cd' commands to
            enter the directory similar to git.
        """
        return ';'.join([f'cd "{x}"' for x in self.get_global_group_values('run_path')])

    def get_global_group_values(self, group):
        """Get a list of values in the global options of the specified group.

        Args:
            group (str): The group name, e.g., 'branch'.

        Return:
            Returns a list of all values for the specified group. The list
            might be empty if there was no option found of that group.
        """
        if group in self.global_group_values:
            return self.global_group_values[group]
        return []

    @staticmethod
    def _parse_any_option(options, args, option_arg_storage, group_values_storage):
        """Parse the next argument(s) trying all known options.

        Args:
            options (list):             List of options, e.g., GLOBAL_OPTIONS.
            args (list):                The arguments starting with the argument to parse.
            option_arg_storage (list):  List to append with the original arguments.
            group_values_storage (map): Map to extend with the values per group.
        """
        for option in options:
            option_matches, consumed_args, option_value = option.parse(args)
            if option_matches:
                option_arg_storage += args[0:consumed_args]
                group_values_storage.setdefault(option.group, []).append(option_value)
                return consumed_args

        # Unknown options are assumed to be boolean flags
        option_arg_storage += args[0:1]
        group_values_storage.setdefault('ignored', []).append(None)
        return 1

    def _parse(self, args):
        """Parse the arguments.

        Args:
            args (list): The arguments to git without the actual git command.
        """
        argv = 0

        # Consume the global options
        while (argv < len(args)) and args[argv].startswith('-'):
            argv += self._parse_any_option(GLOBAL_OPTIONS, args[argv:],
                                           self.global_options, self.global_group_values)

        # Consume the command(s)
        if argv < len(args):
            self.command = args[argv]
            argv += 1

        if self.command in ['lfs', 'submodule']:
            # Consume options until the subcommand is found
            while (argv < len(args)) and args[argv].startswith('-'):
                argv += self._parse_any_option(COMMAND_OPTIONS[self.command], args[argv:],
                                               self.command_options, self.command_group_values)

            if argv < len(args):
                self.command += f"_{args[argv]}"
                argv += 1
            else:
                return

        if self.command in COMMAND_OPTIONS:
            ignore_options = False
            while argv < len(args):
                if ignore_options:
                    self.command_args.append(args[argv])
                    argv += 1
                elif args[argv] == '--':
                    ignore_options = True
                    argv += 1
                elif args[argv].startswith('-'):
                    argv += self._parse_any_option(COMMAND_OPTIONS[self.command], args[argv:],
                                                   self.command_options, self.command_group_values)
                else:
                    self.command_args.append(args[argv])
                    argv += 1


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
