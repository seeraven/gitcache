"""Test the git lfs wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os
import platform

import pytest
from helpers.gitcache_ifc import GitcacheIfc

# ----------------------------------------------------------------------------
#  TEST URL VARIANTS
# ----------------------------------------------------------------------------
LFS_TEST_URLS_DEFAULT = [
    "https://github.com/seeraven/lfs-example",
]
LFS_TEST_URLS_SSH = [
    "git@github.com:seeraven/lfs-example",
    "github.com:seeraven/lfs-example",
    "ssh://git@github.com/seeraven/lfs-example",
    "ssh://github.com/seeraven/lfs-example",
]

if platform.node() in ["Workhorse", "hermes"]:
    LFT_TEST_URLS = LFS_TEST_URLS_DEFAULT + LFS_TEST_URLS_SSH
else:
    LFT_TEST_URLS = LFS_TEST_URLS_DEFAULT


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
@pytest.mark.skipif(os.getenv("IN_GITHUB_ACTION", "0") != "0", reason="Requires working git-lfs environment")
@pytest.mark.parametrize("remote_url", LFT_TEST_URLS)
def test_lfs_fetch(gitcache_ifc: GitcacheIfc, remote_url: str):
    """Test the 'git lfs fetch' command."""
    # Initial clone
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "lfs-example")
    gitcache_ifc.run_ok(["git", "clone", remote_url, checkout])
    db_url = remote_url.replace("git@", "")
    assert 0 == gitcache_ifc.db_field("mirror-updates", db_url)
    assert 1 == gitcache_ifc.db_field("lfs-updates", db_url)

    # Included files by lfs configuration should be checked out
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "included", "first.png"))
    assert gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))

    # git lfs fetch commands that do not update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", db_url)

    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "origin"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", db_url)

    # git lfs fetch commands that update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "--include", "*", "--exclude", ""])
    assert 2 == gitcache_ifc.db_field("lfs-updates", db_url)

    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "origin", "--include", "*", "--exclude", ""])
    assert 3 == gitcache_ifc.db_field("lfs-updates", db_url)

    # git lfs fetch commands update the mirror even if outside the update interval
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "fetch", "--include", "*", "--exclude", ""])
    assert 4 == gitcache_ifc.db_field("lfs-updates", db_url)
    gitcache_ifc.workspace.del_env("GITCACHE_UPDATE_INTERVAL")

    # The excluded file must not be updated by the fetch (only by a pull)
    assert gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))

    # git lfs pull with update of the mirror and checkout of excluded files
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull", "--include", "*", "--exclude", ""])
    assert 5 == gitcache_ifc.db_field("lfs-updates", db_url)
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))


@pytest.mark.skipif(os.getenv("IN_GITHUB_ACTION", "0") != "0", reason="Requires working git-lfs environment")
@pytest.mark.parametrize("remote_url", LFT_TEST_URLS)
def test_lfs_pull(gitcache_ifc: GitcacheIfc, remote_url: str):
    """Test not caching ls-remotes from local filesystem."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "lfs-example")
    gitcache_ifc.run_ok(["git", "clone", remote_url, checkout])
    db_url = remote_url.replace("git@", "")
    assert 0 == gitcache_ifc.db_field("mirror-updates", db_url)
    assert 1 == gitcache_ifc.db_field("lfs-updates", db_url)

    # Included files by lfs configuration should be checked out
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "included", "first.png"))
    assert gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))

    # git lfs pull commands that do not update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", db_url)

    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull", "origin"])
    assert 1 == gitcache_ifc.db_field("lfs-updates", db_url)

    # git lfs pull commands that update the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "lfs", "pull", "--include", "*", "--exclude", ""])
    assert 2 == gitcache_ifc.db_field("lfs-updates", db_url)

    # Excluded entry is now checked out
    assert not gitcache_ifc.str_in_file(b"oid sha256", os.path.join(checkout, "excluded", "first.png"))


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
