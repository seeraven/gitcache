"""Test the git submodule wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

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
    repo = "https://github.com/seeraven/submodule-example.git"
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
    repo = "https://github.com/seeraven/submodule-example.git"
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
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-crt-cpp.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-common.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-io.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-compression.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-cal.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-auth.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-http.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-mqtt.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/s2n.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-checksums.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-event-stream.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-c-s3.git")
    assert 1 == gitcache_ifc.db_field("clones", "https://github.com/awslabs/aws-lc.git")


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


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
