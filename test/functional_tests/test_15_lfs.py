"""Test the git lfs wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_lfs_fetch(gitcache_ifc: GitcacheIfc):
    """Test the 'git lfs fetch' command."""
    # Initial clone
    repo = "https://github.com/seeraven/lfs-example.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "lfs-example")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("lfs-updates", repo)

    # Included files by lfs configuration should be checked out
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "included", "first.png"))
    assert gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))

    # git lfs fetch commands that do not update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", repo)

    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "origin"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", repo)

    # git lfs fetch commands that update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "--include", "*", "--exclude", ""])
    assert 2 == gitcache_ifc.db_field("lfs-updates", repo)

    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "origin", "--include", "*", "--exclude", ""])
    assert 3 == gitcache_ifc.db_field("lfs-updates", repo)

    # git lfs fetch commands update the mirror even if outside the update interval
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "--include", "*", "--exclude", ""])
    assert 4 == gitcache_ifc.db_field("lfs-updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_UPDATE_INTERVAL")

    # The excluded file must not be updated by the fetch (only by a pull)
    assert gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))

    # git lfs pull with update of the mirror and checkout of excluded files
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull", "--include", "*", "--exclude", ""])
    assert 5 == gitcache_ifc.db_field("lfs-updates", repo)
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))


def test_lfs_pull(gitcache_ifc: GitcacheIfc):
    """Test not caching ls-remotes from local filesystem."""
    repo = "https://github.com/seeraven/lfs-example.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "lfs-example")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("lfs-updates", repo)

    # Included files by lfs configuration should be checked out
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "included", "first.png"))
    assert gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))

    # git lfs pull commands that do not update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", repo)

    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull", "origin"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", repo)

    # git lfs pull commands that update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull", "--include", "*", "--exclude", ""])
    assert 2 == gitcache_ifc.db_field("lfs-updates", repo)

    # Excluded entry is now checked out
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
