"""Test the settings output of the application."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_settings_output(gitcache_ifc: GitcacheIfc):
    """Test the settings output when no option is used."""
    result = gitcache_ifc.run_ok([])

    assert "gitcache global settings" in result.stdout
    assert "GITCACHE_CLONE_COMMAND_TIMEOUT" in result.stdout

    assert gitcache_ifc.config_exists()
    assert not gitcache_ifc.db_exists()


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
