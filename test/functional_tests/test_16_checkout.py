"""Test the git checkout wrapping."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_checkout(gitcache_ifc: GitcacheIfc):
    """Test the 'git checkout' command."""
    # Initial clone
    repo = "https://github.com/seeraven/lfs-example.git"
    checkout = os.path.join(gitcache_ifc.workspace.workspace_path, "lfs-example")
    gitcache_ifc.run_ok(["git", "clone", repo, checkout])
    assert 0 == gitcache_ifc.db_field("mirror-updates", repo)
    assert 1 == gitcache_ifc.db_field("lfs-updates", repo)

    # Modify a file and perform checkout call to restore it
    os.unlink(os.path.join(checkout, "README.md"))
    gitcache_ifc.run_ok(["git", "-C", checkout, "checkout", "README.md"])
    assert gitcache_ifc.str_in_file(b"git-lfs", os.path.join(checkout, "README.md"))

    # Checkout to switch to a branch
    gitcache_ifc.run_ok(["git", "-C", checkout, "checkout", "main"])

    # Checkout to switch to a branch should fetch additional files
    gitcache_ifc.run_ok(["git", "-C", checkout, "checkout", "extra_branch"])

    lfs_obj_file = os.path.join(
        *[
            gitcache_ifc.workspace.gitcache_dir_path,
            "mirrors",
            "github.com",
            "seeraven",
            "lfs-example",
            "lfs",
            "objects",
            "c0",
            "c9",
            "c0c955aa4aa976424645d86e82ba4452bb715364171e7db3bf715214b2cfb99d",
        ]
    )
    assert os.path.exists(lfs_obj_file)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
