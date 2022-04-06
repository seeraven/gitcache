# -*- coding: utf-8 -*-
"""
Module for functional tests of gitcache.

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
import os

from .helpers import test_registry


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Registry Access
# -----------------------------------------------------------------------------
def initialize_registry():
    """Initialize the registry by importing all modules within this directory.

    Registry initialization is performed explicit by this call to ensure logging
    is setup correctly beforehand.
    """
    test_registry.initialize_registry(__name__, os.path.dirname(__file__))


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
