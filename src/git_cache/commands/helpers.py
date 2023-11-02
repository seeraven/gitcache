# -*- coding: utf-8 -*-
"""
Helpers for the git commands.

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
import re

from ..command_execution import getstatusoutput
from ..config import Config
from ..global_settings import GITCACHE_DIR

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------
def get_pull_url(git_options):
    """Get the pull url of the remote origin.

    Args:
        git_options (obj): The GitOptions object.

    Return:
        Returns the pull url or None on error.
    """
    command = git_options.get_real_git_with_options()
    command += ["remote", "get-url", "origin"]
    retval, pull_url = getstatusoutput(command)
    if retval == 0:
        return pull_url
    return None


def get_mirror_url(git_options):
    """Derive the mirror URL of a repository.

    Args:
        git_options (obj): The GitOptions object.

    Return:
        Returns the mirror url or None if the repository does not look like
        a mirror.
    """
    pull_url = get_pull_url(git_options)
    if pull_url and pull_url.startswith(GITCACHE_DIR):
        command = git_options.get_real_git_with_options()
        command += ["remote", "get-url", "--push", "origin"]
        retval, push_url = getstatusoutput(command)
        if retval == 0:
            return push_url
        LOG.warning("Can't get push URL of the repository!")
    else:
        LOG.debug("Repository is not managed by gitcache!")

    return None


def get_current_ref(git_options):
    """Get the current ref of a repository.

    Args:
        git_options (obj): The GitOptions object.

    Return:
        Returns the current ref.
    """
    command = git_options.get_real_git_with_options()
    command += ["rev-parse", "--abbrev-ref", "HEAD"]
    retval, ref = getstatusoutput(command)
    if retval == 0:
        return ref
    return None


def use_mirror_for_remote_url(remote_url):
    """Check the given remote URL against the UrlPattern configuration options.

    Args:
        remote_url (str): The remote URL to check.

    Return:
        Returns True if the remote URL should be mirrored.
    """
    config = Config()
    include_re = re.compile(config.get("UrlPatterns", "IncludeRegex"))
    exclude_re = re.compile(config.get("UrlPatterns", "ExcludeRegex"))
    included = include_re.match(remote_url) is not None
    excluded = exclude_re.match(remote_url) is not None
    return included and not excluded


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
