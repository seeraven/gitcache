#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Runner for functional tests of gitcache."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import argparse
import logging
import os
import sys

from tests import initialize_registry
from tests.helpers.test_registry import get_available_tests, get_test_objs
from tests.helpers.test_settings import TestSettings


# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
DESCRIPTION = """
Functional Tests of gitcache
============================

For debugging, set the variable GITCACHE_LOGLEVEL to Debug, e.g.:
    GITCACHE_LOGLEVEL=DEBUG run_tests.py
"""


# -----------------------------------------------------------------------------
# Setup Logging
# -----------------------------------------------------------------------------
def setup_logging(log_level=None, log_format=None):
    """Configure the colored logging.

    Args:
        log_level (str):  The log level, e.g., 'INFO' or 'DEBUG'. The default
                          is to use the environment variable GITCACHE_LOGLEVEL.
        log_format (str): The format string of the logging output. The default
                          is to use the environment variable GITCACHE_LOGFORMAT.
    """
    if log_level is None:
        log_level = os.getenv('GITCACHE_LOGLEVEL', 'INFO')
    if log_format is None:
        log_format = os.getenv('GITCACHE_LOGFORMAT', '%(asctime)s %(message)s')

    log_level_styles = {'debug': {'color': 'cyan'},
                        'info': {'color': 'green'},
                        'warning': {'color': 'yellow'},
                        'error': {'color': 'red'},
                        'critical': {'bold': True, 'color': 'red'}}
    try:
        # pylint: disable=import-outside-toplevel
        import coloredlogs

        coloredlogs.install(level=log_level,
                            level_styles=log_level_styles,
                            fmt=log_format)
    except ModuleNotFoundError:
        logging.basicConfig(level=log_level.upper(),
                            format=log_format)


# -----------------------------------------------------------------------------
# Argument Parser
# -----------------------------------------------------------------------------
def get_parser():
    """Get the argument parser for the :code:`run_tests.py` command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-s", "--save-output",
                        help="Save the gitcache output as reference.",
                        action="store_true",
                        default=False)
    parser.add_argument("-v", "--verbose",
                        help="Be verbose and print all command outputs.",
                        action="store_true",
                        default=False)
    parser.add_argument("-c", "--coverage",
                        help="Use the coverage wrapper.",
                        action="store_true",
                        default=False)
    parser.add_argument("-p", "--pyinstaller",
                        help="Use the pyinstaller generated executable.",
                        action="store_true",
                        default=False)
    parser.add_argument("-t", "--test",
                        help="Execute only the given test. You can specify it multiple times "
                        "to select a set of tests. If not given, all tests are performed. "
                        "Choices: %(choices)s",
                        action="append",
                        default=[],
                        choices=get_available_tests() + ["help"])
    return parser


# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    setup_logging()
    initialize_registry()
    LOG = logging.getLogger(__name__)

    LOG.info("Starting functional tests.")
    args = get_parser().parse_args()

    if "help" in args.test:
        print("Available tests:")
        for test_name in get_available_tests():
            print(f"  - {test_name}")
        sys.exit(0)

    settings = TestSettings(args)

    for test_name, test_obj in iter(get_test_objs(settings).items()):
        if not test_obj.run(test_name, settings):
            sys.exit(1)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
