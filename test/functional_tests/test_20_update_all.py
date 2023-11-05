"""Test the update all functionality."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_update_all(gitcache_ifc: GitcacheIfc):
    """Test the 'git update-mirrors' command."""
    # Update command without any mirrors
    gitcache_ifc.run_ok(["git", "update-mirrors"])
    gitcache_ifc.run_ok(["-u"])

    # Initial clone
    repo = "https://github.com/seeraven/gitcache.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    # Update with 'git update-mirrors'
    gitcache_ifc.run_ok(["git", "update-mirrors"])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)

    # Update with 'gitcache -u'
    gitcache_ifc.run_ok(["-u"])
    assert 2 == gitcache_ifc.db_field("mirror-updates", repo)

    # Explicit update ignores update interval
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    gitcache_ifc.run_ok(["git", "update-mirrors"])
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_UPDATE_INTERVAL")

    # Failed update reflected in return code
    mirror_dir = os.path.join(
        gitcache_ifc.workspace.gitcache_dir_path, "mirrors", "github.com", "seeraven", "gitcache", "git"
    )
    gitcache_ifc.run_ok(
        ["git", "remote", "set-url", "origin", "https://github.com/seeraven/gatcache.git"], cwd=mirror_dir
    )
    gitcache_ifc.run_fail(["git", "update-mirrors"])
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
