"""Test the git submodule wrapping."""

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
def test_submodule_update_single_c(gitcache_ifc: GitcacheIfc):
    """Test the 'submodule init' and 'submodule update' with a single '-C' option."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    c_option = ["-C", checkout]
    _perform_submodule_update_test(gitcache_ifc, c_option=c_option)


def test_submodule_update_multiple_c(gitcache_ifc: GitcacheIfc):
    """Test the 'submodule init' and 'submodule update' with multiple '-C' options."""
    c_option = ["-C", gitcache_ifc.workspace.workspace_path, "-C", "submodules"]
    _perform_submodule_update_test(gitcache_ifc, c_option=c_option)


def test_submodule_update_from_checkout(gitcache_ifc: GitcacheIfc):
    """Test the 'submodule init' and 'submodule update' from the checked out repo."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    _perform_submodule_update_test(gitcache_ifc, cwd=checkout)


def test_submodule_update_module_single_c(gitcache_ifc: GitcacheIfc):
    """Test the 'submodule init mod' and 'submodule update mod' with a single '-C' option."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    c_option = ["-C", checkout]
    _perform_submodule_update_module_test(gitcache_ifc, c_option=c_option)


def test_submodule_update_module_multiple_c(gitcache_ifc: GitcacheIfc):
    """Test the 'submodule init mod' and 'submodule update mod' with multiple '-C' options."""
    c_option = ["-C", gitcache_ifc.workspace.workspace_path, "-C", "submodules"]
    _perform_submodule_update_module_test(gitcache_ifc, c_option=c_option)


def test_submodule_update_module_from_checkout(gitcache_ifc: GitcacheIfc):
    """Test the 'submodule init mod' and 'submodule update mod' from the checked out repo."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    _perform_submodule_update_module_test(gitcache_ifc, cwd=checkout)


def _perform_submodule_update_test(gitcache_ifc: GitcacheIfc, c_option=None, cwd=None):
    """Perform the actual test of 'git submodule init' and 'git submodule update'.

    Args:
        c_option (list): The command arguments to change into the directory.
        cwd (str):       The working directory to execute the command from.
    """
    c_option = c_option or []
    repo = "https://github.com/seeraven/submodule-example"
    repo_sub1 = "https://github.com/seeraven/dmdcache"
    repo_sub2 = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    # Submodule init does not update the mirror nor does it perform any clones
    gitcache_ifc.run_ok(["git"] + c_option + ["submodule", "init"], cwd=cwd)
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)
    assert gitcache_ifc.db_field("clones", repo_sub1) is None
    assert gitcache_ifc.db_field("clones", repo_sub2) is None

    # Submodule update does not update the mirror of this repo ...
    gitcache_ifc.run_ok(["git"] + c_option + ["submodule", "update"], cwd=cwd)
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    # ... but it clones the submodule repos
    assert 1 == gitcache_ifc.db_field("clones", repo_sub1)
    assert 1 == gitcache_ifc.db_field("clones", repo_sub2)

    # Another submodule update updates the mirrors
    gitcache_ifc.run_ok(["git"] + c_option + ["submodule", "update"], cwd=cwd)
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo_sub1)
    assert 1 == gitcache_ifc.db_field("mirror-updates", repo_sub2)
    assert 1 == gitcache_ifc.db_field("updates", repo_sub1)
    assert 1 == gitcache_ifc.db_field("updates", repo_sub1)


def _perform_submodule_update_module_test(gitcache_ifc: GitcacheIfc, c_option=None, cwd=None):
    """Perform the actual test of 'git submodule init <mod>' and 'git submodule update <mod>'.

    Args:
        c_option (list): The command arguments to change into the directory.
        cwd (str):       The working directory to execute the command from.
    """
    c_option = c_option or []
    repo = "https://github.com/seeraven/submodule-example"
    repo_sub1 = "https://github.com/seeraven/dmdcache"
    repo_sub2 = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    # Submodule init does not update the mirror nor does it perform any clones
    path_sub1 = os.path.join(checkout, "dmdcache") if cwd is None else "dmdcache"
    path_sub2 = os.path.join(checkout, "gitcache") if cwd is None else "gitcache"
    gitcache_ifc.run_ok(["git"] + c_option + ["submodule", "init", path_sub1], cwd=cwd)
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)
    assert gitcache_ifc.db_field("clones", repo_sub1) is None
    assert gitcache_ifc.db_field("clones", repo_sub2) is None

    # Submodule update with a path updates only that path
    gitcache_ifc.run_ok(["git"] + c_option + ["submodule", "update", path_sub1], cwd=cwd)
    assert 1 == gitcache_ifc.db_field("clones", repo_sub1)
    assert gitcache_ifc.db_field("clones", repo_sub2) is None

    # Submodule update with --init option also initializes the reference
    gitcache_ifc.run_ok(["git"] + c_option + ["submodule", "update", "--init", path_sub2], cwd=cwd)
    assert 1 == gitcache_ifc.db_field("clones", repo_sub2)


def test_recursive_init(gitcache_ifc: GitcacheIfc):
    """Test 'git submodule update --recursive --init'."""
    repo = "https://github.com/aws/aws-sdk-cpp"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "aws-sdk-cpp")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout, "--single-branch", "--branch", "1.9.188"])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    gitcache_ifc.run_ok(["git", "submodule", "update", "--recursive", "--init"], cwd=checkout)
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-crt-cpp")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-common")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-io")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-compression")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-cal")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-auth")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-http")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-mqtt")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/s2n")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-checksums")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-event-stream")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-s3")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-lc")


def test_exclude(gitcache_ifc: GitcacheIfc):
    """Test 'git submodule update --init' with one submodule not cached."""
    repo = "https://github.com/seeraven/submodule-example"
    repo_sub1 = "https://github.com/seeraven/dmdcache"
    repo_sub2 = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", ".*/github\\.com/seeraven/.*dmdcache")
    gitcache_ifc.run_ok(["git", "-C", checkout, "submodule", "update", "--init"])
    assert gitcache_ifc.db_field("clones", repo_sub1) is None
    assert 1 == gitcache_ifc.db_field("clones", repo_sub2)


def test_include(gitcache_ifc: GitcacheIfc):
    """Test 'git submdoule update --init' with explicitly including one module to be cached."""
    repo = "https://github.com/seeraven/submodule-example"
    repo_sub1 = "https://github.com/seeraven/dmdcache"
    repo_sub2 = "https://github.com/seeraven/gitcache"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_INCLUDE_REGEX", ".*/github\\.com/seeraven/.*dmdcache")
    gitcache_ifc.workspace.set_env("GITCACHE_URLPATTERNS_EXCLUDE_REGEX", "")
    gitcache_ifc.run_ok(["git", "-C", checkout, "submodule", "update", "--init"])
    assert 1 == gitcache_ifc.db_field("clones", repo_sub1)
    assert gitcache_ifc.db_field("clones", repo_sub2) is None


@pytest.mark.parametrize(
    "repo_url,submodule_url,final_submodule_url",
    [
        # Base URL "https://github.com/seeraven/submodule-example"
        (
            "https://github.com/seeraven/submodule-example",
            "https://github.com/seeraven/dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example",
            "../dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example",
            "../something/../dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example/",
            "../dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example/",
            "../dmdcache/",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven",
            "./dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/",
            "./dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/",
            "./dmdcache/",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example",
            "../../seeraven/dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example",
            "https://github.com:443/seeraven/dmdcache",
            "https://github.com:443/seeraven/dmdcache",
        ),
        # Base URL "https://github.com:443/seeraven/submodule-example"
        (
            "https://github.com:443/seeraven/submodule-example",
            "https://github.com/seeraven/dmdcache",
            "https://github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com:443/seeraven/submodule-example",
            "../dmdcache",
            "https://github.com:443/seeraven/dmdcache",
        ),
        (
            "https://github.com:443/seeraven/submodule-example",
            "../../seeraven/dmdcache",
            "https://github.com:443/seeraven/dmdcache",
        ),
    ],
)
def test_relative_submodule_specs(
    gitcache_ifc: GitcacheIfc, repo_url: str, final_submodule_url: str, submodule_url: str
):
    """Test 'git submodule update --init' with different relative repository specifications."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "init", checkout])
    gitcache_ifc.run_ok(["git", "-C", checkout, "remote", "add", "origin", repo_url])
    with open(os.path.join(checkout, ".gitmodules"), "w", encoding="utf-8") as gitmodules:
        gitmodules.write('[submodule "gitcache"]\n')
        gitmodules.write("\tpath = gitcache\n")
        gitmodules.write(f"\turl = {submodule_url}\n")
    gitcache_ifc.run_ok(["git", "-C", checkout, "submodule", "update", "--init"])
    assert 1 == gitcache_ifc.db_field("clones", final_submodule_url)


@pytest.mark.skipif(platform.node() != "Workhorse", reason="Requires known ssh environment")
@pytest.mark.parametrize(
    "repo_url,submodule_url,final_submodule_url",
    [
        # Base URL "https://github.com/seeraven/submodule-example"
        (
            "https://github.com/seeraven/submodule-example",
            "git@github.com:seeraven/dmdcache",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example",
            "ssh://git@github.com/seeraven/dmdcache",
            "ssh://git@github.com/seeraven/dmdcache",
        ),
        (
            "https://github.com/seeraven/submodule-example",
            "ssh://git@github.com:22/seeraven/dmdcache",
            "ssh://git@github.com:22/seeraven/dmdcache",
        ),
        # Base URL "git@github.com:seeraven/submodule-example"
        (
            "git@github.com:seeraven/submodule-example",
            "git@github.com:seeraven/dmdcache",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven/submodule-example",
            "../dmdcache",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven/submodule-example",
            "../dmdcache/",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven/submodule-example/",
            "../dmdcache",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven/submodule-example/",
            "../dmdcache/",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven",
            "./dmdcache",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven/",
            "./dmdcache",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven",
            "./dmdcache/",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven/",
            "./dmdcache/",
            "git@github.com:seeraven/dmdcache",
        ),
        (
            "git@github.com:seeraven/submodule-example",
            "../../seeraven/dmdcache",
            "git@github.com:seeraven/dmdcache",
        ),
        # Base URL "ssh://git@github.com/seeraven/submodule-example"
        (
            "ssh://git@github.com/seeraven/submodule-example",
            "ssh://git@github.com/seeraven/dmdcache",
            "ssh://git@github.com/seeraven/dmdcache",
        ),
        (
            "ssh://git@github.com/seeraven/submodule-example",
            "../dmdcache",
            "ssh://git@github.com/seeraven/dmdcache",
        ),
        (
            "ssh://git@github.com/seeraven/submodule-example",
            "../../seeraven/dmdcache",
            "ssh://git@github.com/seeraven/dmdcache",
        ),
        # Base URL "ssh://git@github.com:22/seeraven/submodule-example"
        (
            "ssh://git@github.com:22/seeraven/submodule-example",
            "ssh://git@github.com:22/seeraven/dmdcache",
            "ssh://git@github.com:22/seeraven/dmdcache",
        ),
        (
            "ssh://git@github.com:22/seeraven/submodule-example",
            "../dmdcache",
            "ssh://git@github.com:22/seeraven/dmdcache",
        ),
        (
            "ssh://git@github.com:22/seeraven/submodule-example",
            "../../seeraven/dmdcache",
            "ssh://git@github.com:22/seeraven/dmdcache",
        ),
    ],
)
def test_relative_submodule_ssh_specs(
    gitcache_ifc: GitcacheIfc, repo_url: str, final_submodule_url: str, submodule_url: str
):
    """Test 'git submodule update --init' with different relative repository specifications."""
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodules")
    gitcache_ifc.run_ok(["git", "init", checkout])
    gitcache_ifc.run_ok(["git", "-C", checkout, "remote", "add", "origin", repo_url])
    with open(os.path.join(checkout, ".gitmodules"), "w", encoding="utf-8") as gitmodules:
        gitmodules.write('[submodule "gitcache"]\n')
        gitmodules.write("\tpath = gitcache\n")
        gitmodules.write(f"\turl = {submodule_url}\n")
    gitcache_ifc.run_ok(["git", "-C", checkout, "submodule", "update", "--init"])
    assert 1 == gitcache_ifc.db_field("clones", final_submodule_url)


def test_submodule_on_orphaned_commit(gitcache_ifc: GitcacheIfc):
    """Test 'git submodule update --init' with a submodule pointing to an orphaned commit."""
    repo = "https://github.com/seeraven/submodule-with-orphaned-commit"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "submodule-with-orphaned-commit")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("clones", repo)
    assert 0 == gitcache_ifc.db_field("updates", repo)

    submodule_repo = "https://github.com/seeraven/orphaned-commits"
    gitcache_ifc.run_ok(["git", "submodule", "update", "--init"], cwd=checkout)
    assert 1 == gitcache_ifc.db_field("mirror-updates", submodule_repo)
    assert 1 == gitcache_ifc.db_field("clones", submodule_repo)
    assert 1 == gitcache_ifc.db_field("updates", submodule_repo)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
