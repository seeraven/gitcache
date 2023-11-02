"""Test the git cleanup command."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os
import time

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_cleanup(gitcache_ifc: GitcacheIfc):
    """Test the 'git cleanup' command."""
    # Initial clone
    repo = "https://github.com/seeraven/gitcache.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    mirror_dir = os.path.join(gitcache_ifc.workspace.gitcache_dir_path, "mirrors", "github.com", "seeraven", "gitcache")
    mirror_file = os.path.join(mirror_dir, "git", "config")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert os.path.exists(mirror_file)
    assert os.path.exists(mirror_dir)

    # Cleanup with 'git cleanup' outside the cleanup time
    gitcache_ifc.run_ok(["git", "cleanup"])
    gitcache_ifc.run_ok(["-c"])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    # Cleanup
    gitcache_ifc.workspace.set_env("GITCACHE_CLEANUP_AFTER", "1")
    time.sleep(2.0)
    gitcache_ifc.run_ok(["git", "cleanup"])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None
    assert not os.path.exists(mirror_file)
    assert not os.path.exists(mirror_dir)

    # Clone again
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert os.path.exists(mirror_file)
    assert os.path.exists(mirror_dir)

    # Cleanup with 'gitcache -c'
    time.sleep(2.0)
    gitcache_ifc.run_ok(["-c"])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None
    gitcache_ifc.workspace.del_env("GITCACHE_CLEANUP_AFTER")
    assert not os.path.exists(mirror_file)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
