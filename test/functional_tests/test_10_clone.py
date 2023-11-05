"""Test cloning git repositories."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_clone_without_arguments(gitcache_ifc: GitcacheIfc):
    """Test of "git clone" without additional arguments."""
    gitcache_ifc.run_fail(["git", "clone"])


def test_clone_error(gitcache_ifc: GitcacheIfc):
    """Test of failing "git clone"."""
    # Note: Cloning from a nonexistant source of github.com asks
    #       for a login on Windows. Therefore, we use a nonexistant URL.
    repo = "https://does.not.exist.com/nonexistant"
    tgt = os.path.join(gitcache_ifc.workspace.workspace_path, "dummy")
    gitcache_ifc.run_fail(["git", "clone", repo, tgt])


def test_clone(gitcache_ifc: GitcacheIfc):
    """Test the normal behaviour of "git clone"."""
    # Initial clone
    repo = "https://github.com/seeraven/gitcache.git"
    tgt = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(tgt)
    assert "master" == gitcache_ifc.get_branch(tgt)

    # Second clone with update of the mirror
    tgt = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")
    gitcache_ifc.run_ok(["git", "clone", repo, tgt])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 2 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(tgt)

    # Third clone without updating the mirror
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    tgt = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache3")
    gitcache_ifc.run_ok(["git", "clone", repo, tgt])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 3 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(tgt)
    gitcache_ifc.workspace.del_env("GITCACHE_UPDATE_INTERVAL")


def test_clone_from_local_fs(gitcache_ifc: GitcacheIfc):
    """Test not caching clones from local filesystem."""
    repo = "https://github.com/seeraven/gitcache.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])

    repo = checkout
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert gitcache_ifc.db_field("clones", repo) is None


def test_clone_branch(gitcache_ifc: GitcacheIfc):
    """Test cloning an explicit branch."""
    repo = "https://github.com/seeraven/scm-autologin-plugin"
    branch = "feature_ownUserType"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "scm-autologin-plugin")
    gitcache_ifc.run_ok(["git", "clone", "--branch", branch, repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(checkout)
    assert branch == gitcache_ifc.get_branch(checkout)

    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "scm-autologin-plugin2")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout, "-b", branch])
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 2 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(checkout)
    assert branch == gitcache_ifc.get_branch(checkout)


def test_clone_tag(gitcache_ifc: GitcacheIfc):
    """Test cloning an explicit tag."""
    repo = "https://github.com/seeraven/scm-autologin-plugin"
    tag = "1.0-scm1.60"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "scm-autologin-plugin")
    gitcache_ifc.run_ok(["git", "clone", "--branch", tag, repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(checkout)
    assert tag == gitcache_ifc.get_tag(checkout)


def test_exclude(gitcache_ifc: GitcacheIfc):
    """Test cloning an excluded url."""
    repo = "https://github.com/seeraven/scm-autologin-plugin"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "scm-autologin-plugin")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", ".*/github\\.com/seeraven/scm-.*")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX")
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX")


def test_include(gitcache_ifc: GitcacheIfc):
    """Test cloning an included url."""
    repo = "https://github.com/seeraven/scm-autologin-plugin"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "scm-autologin-plugin")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*/github\\.com/seeraven/scm-.*")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", "")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX")
    gitcache_ifc.workspace.del_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX")


def test_aborted_clone(gitcache_ifc: GitcacheIfc):
    """Test aborting the first clone command and cloning again."""
    repo = "https://github.com/seeraven/gitcache.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_abort(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None
    assert gitcache_ifc.db_field("clones", repo) is None

    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(checkout)
    assert "master" == gitcache_ifc.get_branch(checkout)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
