# -*- coding: utf-8 -*-
"""
Module for the settings of the functional tests of gitcache.

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
import logging
import platform
from os import path
from shutil import which

from .test_registry import get_available_tests


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Settings Class
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class TestSettings:
    """Encapsulate the test settings."""

    def __init__(self, args):
        """Construct the settings object.

        Args:
            args (obj) - Parser object.
        """
        self.on_windows = platform.system().lower().startswith('win')

        # Assume this file is in the directory <base dir>/tests/functional_tests/tests/helpers.
        # Test base dir is <base dir>/tests/functional_tests
        # Gitcache base dir is <base dir>
        self.test_base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
        self.expected_dir = path.join(self.test_base_dir, 'expected')
        self.gitcache_base_dir = path.dirname(path.dirname(self.test_base_dir))
        LOG.debug("Gitcache base directory: %s", self.gitcache_base_dir)
        LOG.debug("Expected Outputs in:     %s", self.expected_dir)
        LOG.debug("Test base directory:     %s", self.test_base_dir)

        gitcache_bin = path.join(self.gitcache_base_dir, 'gitcache')
        if args.pyinstaller:
            if self.on_windows:
                gitcache_bin = path.join(self.gitcache_base_dir, 'dist', 'gitcache.exe')
            else:
                gitcache_bin = path.join(self.gitcache_base_dir, 'dist', 'gitcache')

        if args.coverage:
            if self.on_windows:
                rcfile = path.join(self.gitcache_base_dir, '.coveragerc-functional-windows')
            else:
                rcfile = path.join(self.gitcache_base_dir, '.coveragerc-functional-linux')
            self.gitcache_cmd = ['coverage', 'run', '--append', f"--rcfile={rcfile}",
                                 gitcache_bin]
        else:
            if self.on_windows and not args.pyinstaller:
                # We need to specify the python executable first
                self.gitcache_cmd = [which("python.exe"), gitcache_bin]
            else:
                self.gitcache_cmd = [gitcache_bin]
        LOG.debug("Gitcache command:        %s", self.gitcache_cmd)

        self.print_output = args.verbose
        LOG.debug("Print output:            %s", self.print_output)

        self.save_output = args.save_output
        LOG.debug("Save output:             %s", self.save_output)

        self.selected_tests = args.test
        if not self.selected_tests:
            self.selected_tests = get_available_tests()
        LOG.debug("Selected tests:          %s", self.selected_tests)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
