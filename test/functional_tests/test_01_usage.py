"""Test the usage output of the application."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_usage(gitcache_ifc: GitcacheIfc):
    """Test the usage output when the '-h' or '--help' option is used."""
    result = gitcache_ifc.run_ok(["--help"])
    result = gitcache_ifc.run_ok(["-h"])

    assert "usage: gitcache" in result.stdout
    assert "Local cache for git repositories to speed up working with large repositories" in result.stdout
    assert "--version" in result.stdout
    assert "Print the version of gitcache." in result.stdout


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
