"""Functional tests for invocation summary log cache markers."""

# ----------------------------------------------------------------------------
#  MODULE IMPORTS
# ----------------------------------------------------------------------------
import os

from helpers.gitcache_ifc import GitcacheIfc


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------
def test_clone_summary_log_miss_create(gitcache_ifc: GitcacheIfc):
    """First clone creates the mirror and logs cache=miss_create."""
    gitcache_ifc.setup_invocation_logs()
    repo = "https://github.com/seeraven/gitcache"
    tgt = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache")

    gitcache_ifc.run_ok(["git", "clone", repo, tgt])

    summary_lines = gitcache_ifc.read_summary_lines()
    assert len(summary_lines) == 1
    assert " mode=gitcache " in f" {summary_lines[0]} "
    assert " cache=miss_create " in f" {summary_lines[0]} "
    assert " exit=0 " in f" {summary_lines[0]} "


def test_clone_summary_log_hit_update(gitcache_ifc: GitcacheIfc):
    """Second clone updates an existing mirror and logs cache=hit_update."""
    gitcache_ifc.setup_invocation_logs()
    repo = "https://github.com/seeraven/gitcache"
    tgt1 = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache1")
    tgt2 = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")

    gitcache_ifc.run_ok(["git", "clone", repo, tgt1])
    gitcache_ifc.run_ok(["git", "clone", repo, tgt2])

    summary_lines = gitcache_ifc.read_summary_lines()
    assert len(summary_lines) == 2
    assert " cache=miss_create " in f" {summary_lines[0]} "
    assert " cache=hit_update " in f" {summary_lines[1]} "


def test_clone_summary_log_hit_skip(gitcache_ifc: GitcacheIfc):
    """Clone with a fresh mirror skips update when the interval is not reached."""
    gitcache_ifc.setup_invocation_logs()
    gitcache_ifc.workspace.set_env("GITCACHE_UPDATE_INTERVAL", "3600")
    repo = "https://github.com/seeraven/gitcache"
    tgt1 = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache1")
    tgt2 = os.path.join(gitcache_ifc.workspace.workspace_path, "gitcache2")

    gitcache_ifc.run_ok(["git", "clone", repo, tgt1])
    gitcache_ifc.run_ok(["git", "clone", repo, tgt2])

    summary_lines = gitcache_ifc.read_summary_lines()
    assert len(summary_lines) == 2
    assert " cache=miss_create " in f" {summary_lines[0]} "
    assert " cache=hit_skip " in f" {summary_lines[1]} "
