"""Test cloning git repositories."""

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
    repo = "https://github.com/seeraven/gitcache"
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

    repo = f"file://{checkout}"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache3")
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
    repo = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_abort(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])
    assert gitcache_ifc.db_field("mirror-updates", repo) is None
    assert gitcache_ifc.db_field("clones", repo) is None

    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert gitcache_ifc.remote_points_to_gitcache(checkout)
    assert "master" == gitcache_ifc.get_branch(checkout)


def test_clone_with_port(gitcache_ifc: GitcacheIfc):
    """Test clone with port specification."""
    repo = "https://github.com:443/seeraven/gitcache"
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", repo])
    assert "github.com_443" in gitcache_ifc.db_field("mirror-dir", repo)


def test_clone_recursive(gitcache_ifc: GitcacheIfc):
    """Test clone with option --recursive to checkout submodules."""
    repo = "https://github.com/seeraven/submodule-example"
    repo_sub1 = "https://github.com/seeraven/dmdcache"
    repo_sub2 = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "clone", "--recursive", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    assert 1 == gitcache_ifc.db_field("clones", repo_sub1)
    assert 1 == gitcache_ifc.db_field("clones", repo_sub2)


def test_clone_recurse_submodules(gitcache_ifc: GitcacheIfc):
    """Test clone with option --recurse-submodules to checkout submodules."""
    repo = "https://github.com/seeraven/submodule-example"
    repo_sub1 = "https://github.com/seeraven/dmdcache"
    repo_sub2 = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "clone", "--recurse-submodules", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    assert 1 == gitcache_ifc.db_field("clones", repo_sub1)
    assert 1 == gitcache_ifc.db_field("clones", repo_sub2)
    assert "master" != gitcache_ifc.get_branch(os.path.join(checkout, "gitcache"))


def test_clone_recurse_submodules_remote_submodules(gitcache_ifc: GitcacheIfc):
    """Test clone with option --recurse-submodules --remote-submodules to checkout submodules."""
    repo = "https://github.com/seeraven/submodule-example"
    repo_sub1 = "https://github.com/seeraven/dmdcache"
    repo_sub2 = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(
        [
            "git",
            "-c",
            "protocol.file.allow=always",
            "clone",
            "--recurse-submodules",
            "--remote-submodules",
            repo,
            checkout,
        ]
    )
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    assert 1 == gitcache_ifc.db_field("clones", repo_sub1)
    assert 1 == gitcache_ifc.db_field("clones", repo_sub2)
    assert "master" == gitcache_ifc.get_branch(os.path.join(checkout, "gitcache"))


@pytest.mark.skipif(platform.node() != "Workhorse", reason="Requires known ssh environment")
@pytest.mark.parametrize(
    "remote_url",
    [
        "git@github.com:seeraven/gitcache.git",
        "github.com:seeraven/gitcache.git",
        "ssh://git@github.com/seeraven/gitcache.git",
        "ssh://github.com/seeraven/gitcache.git",
    ],
)
def test_clone_via_ssh(gitcache_ifc: GitcacheIfc, remote_url: str):
    """Test clone via ssh URLs."""
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", remote_url])
    assert "github.com/seeraven/gitcache" in gitcache_ifc.db_field("mirror-dir", remote_url[:-4])


@pytest.mark.skipif(platform.node() != "Workhorse", reason="Requires known ssh environment")
@pytest.mark.parametrize(
    "remote_url",
    [
        "ssh://git@github.com:22/seeraven/gitcache.git",
        "ssh://github.com:22/seeraven/gitcache.git",
    ],
)
def test_clone_via_ssh_and_port(gitcache_ifc: GitcacheIfc, remote_url: str):
    """Test clone via ssh URLs."""
    gitcache_ifc.run_ok(["git", "-C", gitcache_ifc.workspace.workspace_path, "clone", remote_url])
    assert "github.com_22/seeraven/gitcache" in gitcache_ifc.db_field("mirror-dir", remote_url[:-4])


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
