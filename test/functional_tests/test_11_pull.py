"""Test the git pull wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_pull(gitcache_ifc: GitcacheIfc):
    """Test the "git pull" command."""
    repo = "https://github.com/seeraven/gitcache.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])

    # Pull updates the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "pull"])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 1 == gitcache_ifc.db_field("updates", repo)

    # Pull with multiple -C options updates the mirror as well
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "-C", "gitcache", "pull"])
    assert 2 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 2 == gitcache_ifc.db_field("updates", repo)

    # Pull inside the checked out repository updates the mirror as well
    gitcache_ifc.run_ok(["git", "pull"], cwd=checkout)
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 3 == gitcache_ifc.db_field("updates", repo)

    # Pull without updating the mirror due to update interval
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    gitcache_ifc.run_ok(["git", "pull"], cwd=checkout)
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 4 == gitcache_ifc.db_field("updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_UPDATE_INTERVAL")

    # Pull with repository specification
    gitcache_ifc.run_ok(["git", "-C", checkout, "pull", "origin"])
    assert 4 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 5 == gitcache_ifc.db_field("updates", repo)

    # Pull with repository and ref specification
    gitcache_ifc.run_ok(["git", "-C", checkout, "pull", "origin", "master"])
    assert 5 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 6 == gitcache_ifc.db_field("updates", repo)

    # Do not update mirror if repository does not use the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "remote", "set-url", "origin", repo])
    gitcache_ifc.run_ok(["git", "-C", checkout, "pull"])
    assert 5 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 6 == gitcache_ifc.db_field("updates", repo)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
