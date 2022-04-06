# -*- coding: utf-8 -*-
"""
Module for generating a temporary workspace as a context object.

Copyright:
    2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import copy
import logging
import os
import tempfile


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Context Class
# -----------------------------------------------------------------------------
class TestWorkspace:
    """Provide a temporary workspace on the filesystem."""

    def __init__(self):
        """Construct the empty context object."""
        self.workspace_path = None
        self.gitcache_dir_path = None
        self._tmp_workspace_dir = None
        self._tmp_gitcache_dir = None
        self.env = None

    def __enter__(self):
        """Enter the context."""
        LOG.debug("Enter workspace.")

        self._tmp_workspace_dir = tempfile.TemporaryDirectory(prefix='gitcache_ws_')
        self.workspace_path = self._tmp_workspace_dir.name
        LOG.debug("Created temporary workspace directory: %s", self.workspace_path)

        self._tmp_gitcache_dir = tempfile.TemporaryDirectory(prefix='gitcache_dir_')
        self.gitcache_dir_path = self._tmp_gitcache_dir.name
        LOG.debug("Created temporary gitcache directory:  %s", self.gitcache_dir_path)

        self.env = copy.deepcopy(os.environ)
        self.env['GITCACHE_DIR'] = self.gitcache_dir_path
        self.env['GITCACHE_LOGLEVEL'] = 'INFO'
        self.env['GITCACHE_LOGFORMAT'] = '%(message)s'
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        if self._tmp_workspace_dir:
            self._tmp_workspace_dir.cleanup()
            self._tmp_workspace_dir = None
            self.workspace_path = None
        if self._tmp_gitcache_dir:
            self._tmp_gitcache_dir.cleanup()
            self._tmp_gitcache_dir = None
            self.gitcache_dir_path = None
        self.env = None
        LOG.debug("Closed workspace.")

    def set_env(self, var, value):
        """Set an environment variable to be used during the tests.

        Args:
            var (str):   Name of the environment variable.
            value (str): Value of the environment variable.
        """
        self.env[var] = value

    def del_env(self, var):
        """Remove an environment variable previously set using set_env().

        Args:
            var (str): Name of the environment variable.
        """
        del self.env[var]


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
