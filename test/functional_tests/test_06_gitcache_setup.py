"""Test the gitcache setup of the application."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

import pytest
from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  Helpers
# ----------------------------------------------------------------------------
def skip_complex_executable(gitcache_ifc: GitcacheIfc) -> None:
    """Skip the test if the executable consists of more than one element."""
    if len(gitcache_ifc.executable) > 1:
        pytest.skip("complex gitcache call")


def skip_non_release(gitcache_ifc: GitcacheIfc) -> None:
    """Skip the test if the executable is not a release."""
    skip_complex_executable(gitcache_ifc)
    if "gitcache_v" not in gitcache_ifc.executable[0]:
        pytest.skip("non-pyinstaller executable")


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_symlink_setup(gitcache_ifc: GitcacheIfc, git_exe: str):
    """Test using a symlink called git pointing to gitcache."""
    skip_complex_executable(gitcache_ifc)

    gitcache_ifc.setup_symlink(git_exe)
    result = gitcache_ifc.run_ok(["--version"], executable=git_exe)
    assert "git " in result.stdout
    assert gitcache_ifc.config_exists()


def test_nonexistant_realgit(gitcache_ifc: GitcacheIfc):
    """Test using a non-existant real git command."""
    gitcache_ifc.run_ok(["git", "--version"])  # to create the config file

    gitcache_ifc.workspace.set_env("GITCACHE_REAL_GIT", "/i/do/not/exist")
    result = gitcache_ifc.run_fail(["git", "--version"])
    assert "Can't resolve configured path to the real git command!" in result.stderr


def test_configured_realgit_is_symlink_to_gitcache(gitcache_ifc: GitcacheIfc, git_exe: str):
    """Test setting real git command to gitcache via git symlink."""
    skip_complex_executable(gitcache_ifc)

    gitcache_ifc.run_ok(["git", "--version"])  # to create the config file

    gitcache_ifc.setup_symlink(git_exe)
    gitcache_ifc.workspace.set_env(
        "GITCACHE_REAL_GIT", os.path.join(gitcache_ifc.workspace.workspace_path, "bin", git_exe)
    )
    result = gitcache_ifc.run_fail(["git", "--version"])
    assert "The configured real git command is actually this script!" in result.stderr


def test_copy_setup(gitcache_ifc: GitcacheIfc, git_exe: str):
    """Test using a copy of gitcache called git."""
    skip_non_release(gitcache_ifc)

    gitcache_ifc.setup_copy(git_exe)
    result = gitcache_ifc.run_ok(["--version"], executable=git_exe)
    assert "git " in result.stdout
    assert gitcache_ifc.config_exists()


def test_configured_realgit_is_copy_of_gitcache(gitcache_ifc: GitcacheIfc, git_exe: str):
    """Test setting real git command to copy of gitcache."""
    skip_non_release(gitcache_ifc)

    gitcache_ifc.run_ok(["git", "--version"])  # to create the config file

    gitcache_ifc.setup_copy(git_exe)
    gitcache_ifc.workspace.set_env(
        "GITCACHE_REAL_GIT", os.path.join(gitcache_ifc.workspace.workspace_path, "bin", git_exe)
    )
    result = gitcache_ifc.run_fail(["git", "--version"])
    assert "The configured real git command is actually this script!" in result.stderr


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
