"""Test the git remote add wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_remote_add_origin(gitcache_ifc: GitcacheIfc):
    """Test the 'git remote add origin' command."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")

    # Create initial local git repository
    gitcache_ifc.run_ok(["git", "init", "--initial-branch", "master", checkout])

    # Configure remote
    gitcache_ifc.run_ok(["git", "-C", checkout, "remote", "add", "origin", repo])

    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 0 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(checkout)

    # Perform a pull
    gitcache_ifc.run_ok(["git", "-C", checkout, "pull", "origin", "master"])
    assert "master" == gitcache_ifc.get_branch(checkout)


def test_remote_add_after_clone(gitcache_ifc: GitcacheIfc):
    """Test the 'git remote add origin' command after a clone which should fail."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")

    # Create initial local git repository
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])

    # Configure remote
    gitcache_ifc.run_fail(["git", "-C", checkout, "remote", "add", "origin", repo])


def test_remote_v(gitcache_ifc: GitcacheIfc):
    """Test the 'git remote -v' command after a clone to still work."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")

    # Create initial local git repository
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])

    # Execute git remote -v
    result = gitcache_ifc.run_ok(["git", "remote", "-v"], checkout)
    assert "(fetch)" in result.stdout


def test_remote_add_non_origin(gitcache_ifc: GitcacheIfc):
    """Test the 'git remote add <other>' command."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")

    # Create initial local git repository
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])

    # Configure additional remote
    repo2 = "https://github.com/seeraven/dmdcache"
    gitcache_ifc.run_ok(["git", "-C", checkout, "remote", "add", "remote2", repo2])

    # Ensure the additional remote is not handled by gitcache, as we have no support for it yet
    assert gitcache_ifc.db_field("mirror-updates", repo2) is None
    assert gitcache_ifc.db_field("clones", repo2) is None
