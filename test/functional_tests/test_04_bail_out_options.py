"""Test the bail out options of the application."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_git_version(gitcache_ifc: GitcacheIfc):
    """Test the call as "git --version"."""
    gitcache_ifc.run_ok(["git", "--version"])


def test_git_exec_path(gitcache_ifc: GitcacheIfc):
    """Test the call as "git --exec-path"."""
    gitcache_ifc.run_ok(["git", "--exec-path"])


def test_git_html_path(gitcache_ifc: GitcacheIfc):
    """Test the call as "git --html-path"."""
    gitcache_ifc.run_ok(["git", "--html-path"])


def test_git_man_path(gitcache_ifc: GitcacheIfc):
    """Test the call as "git --man-path"."""
    gitcache_ifc.run_ok(["git", "--man-path"])


def test_git_info_path(gitcache_ifc: GitcacheIfc):
    """Test the call as "git --info-path"."""
    gitcache_ifc.run_ok(["git", "--info-path"])


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
