"""Test the git fetch wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os
import platform

import pytest
from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_fetch(gitcache_ifc: GitcacheIfc):
    """Test the 'git fetch' command."""
    # Initial clone
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])

    # Fetch updates the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch"])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 1 == gitcache_ifc.db_field("updates", repo)

    # Fetch with explicit origin url updates the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch", repo])
    assert 2 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 2 == gitcache_ifc.db_field("updates", repo)

    # Fetch with origin ref updates the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch", "origin"])
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 3 == gitcache_ifc.db_field("updates", repo)

    # Fetch outside update interval does not update the mirror
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch"])
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 4 == gitcache_ifc.db_field("updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_UPDATE_INTERVAL")

    # Fetch from within directory
    gitcache_ifc.run_ok(["git", "fetch", repo], cwd=checkout)
    assert 4 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 5 == gitcache_ifc.db_field("updates", repo)


@pytest.mark.parametrize(
    "remote_url,mirror_dir",
    [
        ("https://github.com/seeraven/gitcache.git", "github.com/seeraven/gitcache"),
        ("https://github.com:443/seeraven/gitcache.git", "github.com_443/seeraven/gitcache"),
    ],
)
def test_fetch_in_empty_repo(gitcache_ifc: GitcacheIfc, remote_url: str, mirror_dir: str):
    """Test fetching in a newly initialized git repo."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "init", checkout])
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch", remote_url[:-4]])
    assert 0 == gitcache_ifc.db_field("mirror-updates", remote_url[:-4])
    assert 0 == gitcache_ifc.db_field("clones", remote_url[:-4])
    assert 1 == gitcache_ifc.db_field("updates", remote_url[:-4])
    assert mirror_dir in gitcache_ifc.db_field("mirror-dir", remote_url[:-4])


@pytest.mark.skipif(platform.node() != "Workhorse", reason="Requires known ssh environment")
@pytest.mark.parametrize(
    "remote_url,mirror_dir",
    [
        ("git@github.com:seeraven/gitcache.git", "github.com/seeraven/gitcache"),
        ("github.com:seeraven/gitcache.git", "github.com/seeraven/gitcache"),
        ("ssh://git@github.com/seeraven/gitcache.git", "github.com/seeraven/gitcache"),
        ("ssh://github.com/seeraven/gitcache.git", "github.com/seeraven/gitcache"),
        ("ssh://git@github.com:22/seeraven/gitcache.git", "github.com_22/seeraven/gitcache"),
        ("ssh://github.com:22/seeraven/gitcache.git", "github.com_22/seeraven/gitcache"),
    ],
)
def test_fetch_in_empty_repo_on_workhorse(gitcache_ifc: GitcacheIfc, remote_url: str, mirror_dir: str):
    """Test fetching in a newly initialized git repo."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "init", checkout])
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch", remote_url])
    assert 0 == gitcache_ifc.db_field("mirror-updates", remote_url[:-4])
    assert 0 == gitcache_ifc.db_field("clones", remote_url[:-4])
    assert 1 == gitcache_ifc.db_field("updates", remote_url[:-4])
    assert mirror_dir in gitcache_ifc.db_field("mirror-dir", remote_url[:-4])


def test_fetch_from_local_fs(gitcache_ifc: GitcacheIfc):
    """Test not caching fetches from local filesystem."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])

    checkout2 = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")
    gitcache_ifc.run_ok(["git", "clone", checkout, checkout2])
    gitcache_ifc.run_ok(["git", "remote", "set-url", "origin", repo], cwd=checkout)

    gitcache_ifc.run_ok(["git", "-C", checkout2, "fetch"])
    assert gitcache_ifc.db_field("clones", checkout) is None

    gitcache_ifc.run_ok(["git", "-C", checkout2, "fetch", checkout])
    assert gitcache_ifc.db_field("clones", checkout) is None

    gitcache_ifc.run_ok(["git", "-C", checkout2, "fetch", f"file://{checkout}"])
    assert gitcache_ifc.db_field("clones", f"file://{checkout}") is None


def test_exclude(gitcache_ifc: GitcacheIfc):
    """Test fetching an excluded url."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", ".*/github\\.com/.*")
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch", repo])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX")
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX")


def test_include(gitcache_ifc: GitcacheIfc):
    """Test fetching an included url."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*/github\\.com/.*")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", "")
    gitcache_ifc.run_ok(["git", "-C", checkout, "fetch", repo])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 1 == gitcache_ifc.db_field("updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX")
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX")


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
