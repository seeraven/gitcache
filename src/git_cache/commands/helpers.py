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
    if pull_url and (pull_url.startswith(GITCACHE_DIR) or pull_url.startswith(f"file://{GITCACHE_DIR}")):
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


def resolve_submodule_url(repo_url, submodule_url):
    """Resolve possibly relative submodule url to a full submodule git url.

    Args:
        repo_url (str): url of the repository holding a submodule.
        submodule_url (str): url of the submodule.

    Return:
        A resolved/normalized git url of the submodule.
    """
    # Note: Relative submodules use git-specific method to join url
    #       As per git documentation, relative url may only start with
    #       './' or '../'. Since git urls are not exactly same as regular urls -
    #       both urllib.parse.urljoin and posixpath.normpath do not perform well
    #       when need to combine a relative git url with all of the allowed
    #       absolute git urls.
    #       This routine mimics how git would resolve submodule url.

    if not submodule_url.startswith("./") and not submodule_url.startswith("../"):
        return submodule_url

    repo_url = repo_url.rstrip("/")

    while True:
        if submodule_url.startswith("./"):
            submodule_url = submodule_url[2:]
        elif submodule_url.startswith("../"):
            submodule_url = submodule_url[3:]
            last_idx = max(repo_url.rfind("/"), repo_url.rfind(":"))

            if last_idx > 2 and repo_url[last_idx - 2 : last_idx + 1] == "://":
                # Stop in case if we reached the protocol separator
                continue
            if last_idx != -1:
                if repo_url[last_idx] == ":":
                    # Don't ever go past ":" separator
                    repo_url = repo_url[: last_idx + 1]
                    continue
                repo_url = repo_url[:last_idx]
        else:
            break

    # Add url separator, unless we've reached the ":",
    # which is a separator on its own
    if not repo_url.endswith(":"):
        repo_url += "/"

    return repo_url + submodule_url


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
