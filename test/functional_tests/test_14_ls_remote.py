"""Test the git ls-remote wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_ls_remote(gitcache_ifc: GitcacheIfc):
    """Test the 'git ls-remote' command."""
    # Initial clone
    repo = "https://github.com/seeraven/gitcache.git"
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


def test_ls_remote_from_local_fs(gitcache_ifc: GitcacheIfc):
    """Test not caching ls-remotes from local filesystem."""
    repo = "https://github.com/seeraven/gitcache.git"
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


def test_exclude(gitcache_ifc: GitcacheIfc):
    """Test ls-remote on an excluded url."""
    repo = "https://github.com/seeraven/gitcache.git"
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
    repo = "https://github.com/seeraven/gitcache.git"
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
