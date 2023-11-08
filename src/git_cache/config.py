# -*- coding: utf-8 -*-
"""
Module for handling the settings of gitcache.

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
import configparser
import logging
import os
import platform
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import pytimeparse

from .command_execution import getstatusoutput
from .global_settings import GITCACHE_DIR

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Type Aliases
# -----------------------------------------------------------------------------
ConfigItemValue = Union[str, int, bool]
ConfigItemConverter = Callable[[str], ConfigItemValue]
EnvMap = Dict[str, Dict[str, str]]
ConverterMap = Dict[str, Dict[str, ConfigItemConverter]]


# -----------------------------------------------------------------------------
# Converter Functions
# -----------------------------------------------------------------------------
def _str_to_regex(string: str) -> str:
    """Convert a string to a regex pattern with special treatment of an empty string."""
    if string:
        return string
    return "a^"  # This pattern should never match


def _str_to_bool(string: str) -> bool:
    """Convert a string to a boolean value."""
    if string.upper() in ["1", "ON", "TRUE", "YES"]:
        return True
    return False


def _str_to_seconds(string: str) -> int:
    """Convert a string to a seconds value."""
    seconds = pytimeparse.parse(string)
    if seconds is None:
        try:
            seconds = int(string.strip())
        except ValueError:
            seconds = 0
    return seconds


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def has_git_lfs_cmd() -> bool:
    """Check whether this host has the git-lfs command available.

    Return:
        Returns True if the git-lfs command is available.
    """
    attribute = "has_git_lfs"
    if not hasattr(has_git_lfs_cmd, attribute):
        retval, _ = getstatusoutput(["git-lfs", "version"])
        setattr(has_git_lfs_cmd, attribute, retval == 0)
    return getattr(has_git_lfs_cmd, attribute)


# -----------------------------------------------------------------------------
# Default Functions
# -----------------------------------------------------------------------------
def _get_this_script_path() -> Path:
    """Get the full path to the currently running gitcache resolving all symlinks."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return (Path(__file__).parent.parent / "gitcache").resolve()


def _find_git() -> str:
    """Locate the real git command.

    Return:
        Returns the full path to the real git command. If the command is not
        found, return the platform dependend default value and log a warning.
    """
    path = os.getenv("PATH", "")
    on_windows = platform.system().lower().startswith("win")
    cmd = "git.exe" if on_windows else "git"
    this_script = _get_this_script_path()
    for candidate_path in path.split(os.path.pathsep):
        candidate_exe = Path(candidate_path) / cmd
        try:
            resolved_exe = candidate_exe.resolve(strict=True)
        except FileNotFoundError:
            continue

        if resolved_exe != this_script:
            LOG.debug("Found real git command as %s (resolving to %s).", candidate_exe, resolved_exe)
            return str(candidate_exe)

    LOG.warning("Can't find git command! Please specify manually in the config file!")
    return "/usr/bin/git"


# -----------------------------------------------------------------------------
# Class Definition
# -----------------------------------------------------------------------------
class ConfigItem:
    """All information about a configuration item.

    Attributes:
        section (str):       The section in the configuration file.
        option (str):        The option name.
        default:             The default value.
        converter:           Converter from string to the return value.
        env (str):           The name of the environment variable or None.
    """

    camel_to_snake = re.compile(r"(?<!^)(?=[A-Z])")

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        section: str,
        option: str,
        default: ConfigItemValue,
        converter: ConfigItemConverter = _str_to_seconds,
        env: str = "auto",
    ) -> None:
        """Construct a configuration item.

        Args:
            section (str): The section in the configuration file.
            option (str):  The option name.
            default:       The default value.
            converter:     The converter used to convert the string to the
                           return value.
            env (str):     The name of the environment variable. If set to
                           None, no environment variable will be registered.
                           If set to 'auto', the name of the environment variable
                           is constructed as 'GITCACHE_<SECTION>_<OPTION>'.
        """
        self.section = section
        self.option = option
        self.default = default
        self.converter = converter
        self.env = env
        if self.env == "auto":
            self.env = f"GITCACHE_{self.section.upper()}_{self._get_snake_upper(self.option)}"

    @staticmethod
    def _get_snake_upper(camel: str) -> str:
        """Convert the given CamelCase string into a SNAKE_CASE string.

        Args:
            camel (str): The CamelCase string.

        Return:
            Returns the SNAKE_CASE string.
        """
        return ConfigItem.camel_to_snake.sub("_", camel).upper()

    def add_to_configparser(self, config: configparser.ConfigParser) -> None:
        """Add the configuration item to the configparser.ConfigParser object.

        Args:
            config (configparser.ConfigParser): The config parser object.
        """
        if self.section not in config.sections():
            config.add_section(self.section)

        config.set(self.section, self.option, str(self.default))

    def add_to_env_keys(self, env_keys: EnvMap) -> None:
        """Add the configuration item to the env_keys map.

        Args:
            env_keys (map): The env_keys map to add the environment key.
        """
        if self.env:
            env_section = self.section.upper()
            env_option = self.option.upper()
            if env_section not in env_keys:
                env_keys[env_section] = {}
            env_keys[env_section][env_option] = self.env

    def add_to_converters(self, converters: ConverterMap) -> None:
        """Add the configuration item to the converters map.

        Args:
            converters (map): The converters map to add the converter function.
        """
        section = self.section.upper()
        option = self.option.upper()
        if section not in converters:
            converters[section] = {}
        converters[section][option] = self.converter


class Config:
    """The configuration of gitcache."""

    def __init__(self) -> None:
        """Initialize the configuration.

        Initialize the configuration by setting the default values and
        loading the global configuration file.
        """
        self.items: List[ConfigItem] = []
        self.items.append(ConfigItem("System", "RealGit", _find_git(), converter=str, env="GITCACHE_REAL_GIT"))

        self.items.append(ConfigItem("MirrorHandling", "UpdateInterval", "0 seconds", env="GITCACHE_UPDATE_INTERVAL"))
        self.items.append(ConfigItem("MirrorHandling", "CleanupAfter", "14 days", env="GITCACHE_CLEANUP_AFTER"))

        self.items.append(ConfigItem("UrlPatterns", "IncludeRegex", ".*", converter=_str_to_regex))
        self.items.append(ConfigItem("UrlPatterns", "ExcludeRegex", "", converter=_str_to_regex))

        self.items.append(ConfigItem("Command", "WarnIfLockedFor", "10 seconds"))
        self.items.append(ConfigItem("Command", "CheckInterval", "2 seconds"))
        self.items.append(ConfigItem("Command", "LockTimeout", "1 hour"))

        self.items.append(ConfigItem("Clone", "Retries", 3, converter=int))
        self.items.append(ConfigItem("Clone", "CommandTimeout", "1 hour"))
        self.items.append(ConfigItem("Clone", "OutputTimeout", "5 minutes"))

        self.items.append(ConfigItem("Update", "Retries", 3, converter=int))
        self.items.append(ConfigItem("Update", "CommandTimeout", "1 hour"))
        self.items.append(ConfigItem("Update", "OutputTimeout", "5 minutes"))

        self.items.append(ConfigItem("GC", "Retries", 3, converter=int))
        self.items.append(ConfigItem("GC", "CommandTimeout", "1 hour"))
        self.items.append(ConfigItem("GC", "OutputTimeout", "5 minutes"))

        self.items.append(ConfigItem("LFS", "Retries", 3, converter=int))
        self.items.append(ConfigItem("LFS", "CommandTimeout", "1 hour"))
        self.items.append(ConfigItem("LFS", "OutputTimeout", "5 minutes"))
        self.items.append(ConfigItem("LFS", "PerMirrorStorage", True, converter=_str_to_bool))

        self.config = configparser.ConfigParser()
        self.env_keys: EnvMap = {}
        self.converters: ConverterMap = {}
        for item in self.items:
            item.add_to_configparser(self.config)
            item.add_to_env_keys(self.env_keys)
            item.add_to_converters(self.converters)

        if not self.load(os.path.join(GITCACHE_DIR, "config")):
            self.save(os.path.join(GITCACHE_DIR, "config"))
        else:
            self._check_real_git()

    def _check_real_git(self) -> None:
        """Check the configured real git command."""
        try:
            realgit = Path(str(self.get("System", "RealGit"))).resolve(strict=True)
        except FileNotFoundError as exception:
            LOG.error("Can't resolve configured path to the real git command!")
            LOG.error("Configuration file:  %s", os.path.join(GITCACHE_DIR, "config"))
            LOG.error("Configured real git: %s", self.get("System", "RealGit"))
            LOG.error("Error:               %s", str(exception))
            LOG.error(
                "Required action:     Please change the entry in the configuration file "
                "to point to the real git executable!"
            )
            sys.exit(1)

        if _get_this_script_path() == realgit:
            LOG.error("The configured real git command is actually this script!")
            LOG.error("Configuration file:  %s", os.path.join(GITCACHE_DIR, "config"))
            LOG.error("Configured real git: %s", self.get("System", "RealGit"))
            LOG.error(
                "Required action:     Please change the entry in the configuration file "
                "to point to the real git executable!"
            )
            sys.exit(1)

    def get(self, section: str, option: str) -> Optional[ConfigItemValue]:
        """Get a configuration value.

        Args:
            section (str): The section, e.g., 'Clone'.
            option (str):  The option, e.g., 'Retries'.
        Return:
            Returns the current value of the specified option or None if it is not found.
        """
        str_value: Optional[str] = None
        env_key = self.env_keys.get(section.upper(), {}).get(option.upper())
        converter = self.converters.get(section.upper(), {}).get(option.upper())

        if env_key:
            str_value = os.getenv(env_key, None)
        if str_value is None:
            str_value = self.config.get(section, option)
        if str_value is None:
            return None
        if converter:
            return converter(str_value)
        return str_value

    def load(self, filename: str) -> bool:
        """Load the configuration file.

        Args:
            filename (str): The file to read.
        Return:
            Returns True if the configuration file was found and loaded.
        """
        if os.path.exists(filename):
            LOG.debug("Loading configuration file %s.", filename)
            with open(filename, "r", encoding="utf-8") as file_handle:
                self.config.read_file(file_handle, source=filename)
                return True

        LOG.debug("Can't load configuration file %s as it does not exist yet!", filename)
        return False

    def save(self, filename: str) -> None:
        """Save the configuration file.

        Args:
            filename (str): The file to save.
        """
        LOG.info("Save configuration file %s.", filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as file_handle:
            self.config.write(file_handle)

    def __str__(self) -> str:
        """Get a string representation of the current configuration.

        Return:
            Returns the string representation.
        """
        ret = ""
        for section in sorted(self.config.sections()):
            if ret:
                ret += "\n"

            ret += f"{section}:\n"
            for option in sorted(self.config[section]):
                env_key = self.env_keys.get(section.upper(), {}).get(option.upper())
                if env_key:
                    ret += f" {option : <20} = {self.config[section][option] : <20} ({env_key})\n"
                else:
                    ret += f" {option : <20} = {self.config[section][option]}\n"
        return ret


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
