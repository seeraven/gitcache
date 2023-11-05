"""Test the gitcache version output of the application."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_gitcache_version(gitcache_ifc: GitcacheIfc):
    """Test the call as "gitcache --version"."""
    gitcache_ifc.run_ok(["--version"])
    assert not gitcache_ifc.config_exists()


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
