"""Test the git delete-mirror command."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_delete(gitcache_ifc: GitcacheIfc):
    """Test the 'git delete-mirror' command."""
    # Initial clone
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    # Delete giving the URL
    gitcache_ifc.run_ok(["git", "delete-mirror", repo])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None

    # Delete giving the path
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    mirror_dir = os.path.join(gitcache_ifc.workspace.gitcache_dir_path, "mirrors", "github.com", "seeraven", "gitcache")
    gitcache_ifc.run_ok(["git", "delete-mirror", mirror_dir])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None

    # Delete using 'gitcache -d' command
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache3")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    gitcache_ifc.run_ok(["-d", repo])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None

    # Delete using 'gitcache -d' command giving the path
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache4")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    gitcache_ifc.run_ok(["-d", mirror_dir])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None

    # Delete using invalid URL
    gitcache_ifc.run_fail(["-d", "https://github.com/seeraven/gatcache"])

    # Delete using invalid path
    mirror_dir = os.path.join(gitcache_ifc.workspace.gitcache_dir_path, "mirrors", "github.com", "seeraven", "gatcache")
    gitcache_ifc.run_fail(["-d", mirror_dir])

    # Delete more than one mirror at once
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache5")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    repo2 = "https://github.com/seeraven/submodule-example"
    checkout2 = os.path.join(gitcache_ifc.workspace.workspace_path, "submodule-example")
    gitcache_ifc.run_ok(["git", "clone", repo2, checkout2])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo2)

    gitcache_ifc.run_ok(["-d", repo, "-d", repo2])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None
    assert gitcache_ifc.db_field("mirror-updates", repo2) is None


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
