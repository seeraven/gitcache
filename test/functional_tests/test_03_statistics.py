"""Test the statistics output of the application."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_initial_statistics_output(gitcache_ifc: GitcacheIfc):
    """Test the initial statistics output."""
    result = gitcache_ifc.run_ok(["-s"])
    init_stats_output = """Total:
  Mirror Updates:       0
  Mirror Updates (LFS): 0
  Clones from Mirror:   0
  Updates from Mirror:  0
"""
    assert init_stats_output in result.stdout
    assert not gitcache_ifc.config_exists()
    assert not gitcache_ifc.db_exists()


def test_statistics_output_after_clone(gitcache_ifc: GitcacheIfc):
    """Test the statistics output after a clone."""
    # Clone a repository
    repo = "https://github.com/seeraven/gitcache"
    tgt = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, tgt])
    assert gitcache_ifc.config_exists()
    assert gitcache_ifc.db_exists()
    assert 1 == gitcache_ifc.db_field("clones", repo)

    # Statistics after the clone
    result = gitcache_ifc.run_ok(["-s"])
    clone_stats_output = """Mirror of https://github.com/seeraven/gitcache:
  Mirror Updates:       0
  Mirror Updates (LFS): 1
  Clones from Mirror:   1
  Updates from Mirror:  0

Total:
  Mirror Updates:       0
  Mirror Updates (LFS): 1
  Clones from Mirror:   1
  Updates from Mirror:  0
"""
    assert clone_stats_output in result.stdout


def test_cleared_statistics_output(gitcache_ifc: GitcacheIfc):
    """Test the statistics output after clearing it."""
    # Clone a repository
    repo = "https://github.com/seeraven/gitcache"
    tgt = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")
    gitcache_ifc.run_ok(["git", "clone", repo, tgt])
    assert 1 == gitcache_ifc.db_field("clones", repo)

    # Clear statistics
    gitcache_ifc.run_ok(["-z"])
    assert 0 == gitcache_ifc.db_field("clones", repo)

    # Statistics output after clearing the statistics
    result = gitcache_ifc.run_ok(["-s"])
    zeroed_stats_output = """Mirror of https://github.com/seeraven/gitcache:
  Mirror Updates:       0
  Mirror Updates (LFS): 0
  Clones from Mirror:   0
  Updates from Mirror:  0

Total:
  Mirror Updates:       0
  Mirror Updates (LFS): 0
  Clones from Mirror:   0
  Updates from Mirror:  0
"""
    assert zeroed_stats_output in result.stdout


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
