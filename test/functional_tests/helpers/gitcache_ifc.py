"""
Module for providing a test interface to gitcache.

Copyright:
    2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import os
import platform
import signal
import subprocess
import time
from typing import Any, List

from .workspace import Workspace


# -----------------------------------------------------------------------------
# Interface Class
# -----------------------------------------------------------------------------
class GitcacheIfc:
    """Interface to run gitcache and check its state."""

    def __init__(self, executable: List[str], workspace: Workspace) -> None:
        """Create the interface to gitcache."""
        self._executable = executable
        self.workspace = workspace

    def run(self, args: List[str], cwd=None) -> subprocess.CompletedProcess:
        """Run gitcache and return the result."""
        return subprocess.run(
            self._executable + args,
            shell=False,
            text=True,
            check=False,
            env=self.workspace.env,
            cwd=cwd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def run_ok(self, args: List[str], cwd=None) -> subprocess.CompletedProcess:
        """Run gitcache and return the result. Also assert a return code of 0."""
        result = self.run(args, cwd)
        if result.returncode != 0:
            print(f"Command {self._executable + args} failed:")
        print(f"  Stdout: {result.stdout}")
        print(f"  Stderr: {result.stderr}")
        assert 0 == result.returncode
        return result

    def run_fail(self, args: List[str], cwd=None) -> subprocess.CompletedProcess:
        """Run gitcache and return the result. Also assert a return code of non-zero."""
        result = self.run(args, cwd)
        assert 0 != result.returncode
        return result

    def run_abort(self, args: List[str], cwd=None, killtime=0.1) -> subprocess.CompletedProcess:
        """Run gitcache and abort it."""
        with subprocess.Popen(
            self._executable + args,
            shell=False,
            env=self.workspace.env,
            cwd=cwd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        ) as process:
            time.sleep(killtime)
            if platform.system().lower().startswith("win"):
                process.terminate()
            else:
                process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate()
            process.wait()
            result: subprocess.CompletedProcess = subprocess.CompletedProcess(process.args, process.returncode)
            result.stdout = stdout
            result.stderr = stderr
        return result

    def config_exists(self) -> bool:
        """Check if the gitcache config file exists."""
        config_path = os.path.join(self.workspace.gitcache_dir_path, "config")
        return os.path.exists(config_path)

    def db_exists(self) -> bool:
        """Check if the gitcache database file exists."""
        db_path = os.path.join(self.workspace.gitcache_dir_path, "db")
        return os.path.exists(db_path)

    def db_field(self, field: str, url: str) -> Any:
        """Get the database field for an url. If it does not exist None is returned.

        Available database fields are:
          - last-update-time
          - mirror-updates
          - lfs-updates
          - clones
          - updates
          - mirror-dir
        """
        db_path = os.path.join(self.workspace.gitcache_dir_path, "db")
        if not os.path.exists(db_path):
            return None

        with open(db_path, "r", encoding="utf-8") as file_handle:
            # pylint: disable=eval-used
            database = eval(file_handle.read())

        for mirror_dir in database:
            if database[mirror_dir]["url"].startswith(url):
                if field == "mirror-dir":
                    return mirror_dir
                if field in database[mirror_dir]:
                    return database[mirror_dir][field]
        return None

    def get_remote(self, checkout_dir: str) -> str:
        """Get the remote of the given checkout directory."""
        command = ["git", "-C", checkout_dir, "remote", "get-url", "origin"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False, check=True)
        return result.stdout.decode().strip()

    def get_branch(self, checkout_dir: str) -> str:
        """Get the current branch of the given checkout directory."""
        command = ["git", "-C", checkout_dir, "rev-parse", "--abbrev-ref", "HEAD"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False, check=True)
        return result.stdout.decode().strip()

    def get_tag(self, checkout_dir: str) -> str:
        """Get the current tag of the given checkout directory."""
        command = ["git", "-C", checkout_dir, "describe", "--tags"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False, check=True)
        return result.stdout.decode().strip()

    def remote_points_to_gitcache(self, checkout_dir: str) -> bool:
        """Check if the remote of the given checkout directory points to the gitcache dir."""
        return self.get_remote(checkout_dir).startswith(self.workspace.gitcache_dir_path)

    def str_in_file(self, needle: bytes, filename: str) -> bool:
        """Check for the given needle string in the file."""
        with open(filename, "rb") as file_handle:
            content = file_handle.read()
        return needle in content


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
