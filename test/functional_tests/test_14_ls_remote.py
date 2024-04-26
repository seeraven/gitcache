"""Test the git ls-remote wrapping."""

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
def test_ls_remote(gitcache_ifc: GitcacheIfc):
    """Test the 'git ls-remote' command."""
    # Initial clone
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])

    # ls-remote updates the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "ls-remote"])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    # ls-remote specifying the remote url updates the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "ls-remote", repo])
    assert 2 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    # ls-remote specifying the origin ref updates the mirror
    gitcache_ifc.run_ok(["git", "-C", checkout, "ls-remote", "origin"])
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    # ls-remote outside update interval does not update the mirror
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    gitcache_ifc.run_ok(["git", "-C", checkout, "ls-remote"])
    assert 3 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_UPDATE_INTERVAL")

    # ls-remote from within directory
    gitcache_ifc.run_ok(["git", "ls-remote"], cwd=checkout)
    assert 4 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)


@pytest.mark.parametrize(
    "remote_url,mirror_dir",
    [
        ("https://github.com/seeraven/gitcache.git", "github.com/seeraven/gitcache"),
        ("https://github.com:443/seeraven/gitcache.git", "github.com_443/seeraven/gitcache"),
    ],
)
def test_ls_remote_without_initial_clone(gitcache_ifc: GitcacheIfc, remote_url: str, mirror_dir: str):
    """Test the 'git ls-remote' command without an initial checkout."""
    gitcache_ifc.run_ok(["git", "ls-remote", remote_url])
    assert 0 == gitcache_ifc.db_field("mirror-updates", remote_url[:-4])
    assert 0 == gitcache_ifc.db_field("clones", remote_url[:-4])
    assert 0 == gitcache_ifc.db_field("updates", remote_url[:-4])
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
def test_ls_remote_without_initial_clone_on_workhorse(gitcache_ifc: GitcacheIfc, remote_url: str, mirror_dir: str):
    """Test the 'git ls-remote' command without an initial checkout."""
    gitcache_ifc.run_ok(["git", "ls-remote", remote_url])
    assert 0 == gitcache_ifc.db_field("mirror-updates", remote_url[:-4])
    assert 0 == gitcache_ifc.db_field("clones", remote_url[:-4])
    assert 0 == gitcache_ifc.db_field("updates", remote_url[:-4])
    assert mirror_dir in gitcache_ifc.db_field("mirror-dir", remote_url[:-4])


def test_ls_remote_from_local_fs(gitcache_ifc: GitcacheIfc):
    """Test not caching ls-remotes from local filesystem."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)

    checkout2 = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")
    gitcache_ifc.run_ok(["git", "clone", checkout, checkout2])
    gitcache_ifc.run_ok(["git", "remote", "set-url", "origin", repo], cwd=checkout)
    assert gitcache_ifc.db_field("mirror-updates", checkout) is None

    # ls-remote on unmanaged checkout does not update the remote repository
    gitcache_ifc.run_ok(["git", "-C", checkout2, "ls-remote"])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert gitcache_ifc.db_field("mirror-updates", checkout) is None

    # Same behaviour when using the origin as an argument
    gitcache_ifc.run_ok(["git", "ls-remote", checkout2])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert gitcache_ifc.db_field("mirror-updates", checkout2) is None

    checkout2 = f"file://{checkout2}"
    gitcache_ifc.run_ok(["git", "ls-remote", checkout2])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert gitcache_ifc.db_field("mirror-updates", checkout2) is None


def test_exclude(gitcache_ifc: GitcacheIfc):
    """Test ls-remote on an excluded url."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", ".*/github\\.com/.*")
    gitcache_ifc.run_ok(["git", "-C", checkout, "ls-remote", repo])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX")
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX")


def test_include(gitcache_ifc: GitcacheIfc):
    """Test ls-remote on an included url."""
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*/github\\.com/.*")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", "")
    gitcache_ifc.run_ok(["git", "-C", checkout, "ls-remote", repo])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX")
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX")


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
