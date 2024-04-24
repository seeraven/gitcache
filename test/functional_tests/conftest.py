"""Configuration of pytest for functional tests."""

# pylint: disable=redefined-outer-name

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os
import shutil
from typing import List

import helpers.gitcache_ifc
import helpers.workspace
import pytest


# ----------------------------------------------------------------------------
#  PYTEST ADDITIONAL OPTIONS
# ----------------------------------------------------------------------------
def pytest_addoption(parser):
    """Add options to the pytest argument parser."""
    parser.addoption(
        "--executable",
        action="store",
        type=str,
        help="The gitcache executable. Default: %(default)s",
        default="src/gitcache",
    )


@pytest.fixture(scope="session")
def executable(pytestconfig) -> List[str]:
    """Fill the executable argument as a list of strings from the pytest option."""
    abs_args = []
    for arg in pytestconfig.getoption("executable").split(" "):
        if os.path.exists(arg):
            abs_args.append(os.path.abspath(arg))
        else:
            abs_args.append(shutil.which(arg))
    return abs_args


@pytest.fixture
def workspace():
    """Return a temporary workspace for gitcache to use."""
    with helpers.workspace.Workspace() as new_workspace:
        yield new_workspace


@pytest.fixture
def gitcache_ifc(executable: List[str], workspace: helpers.workspace.Workspace) -> helpers.gitcache_ifc.GitcacheIfc:
    """Return the high-level interface to gitcache."""
    return helpers.gitcache_ifc.GitcacheIfc(executable, workspace)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
