"""
Module for managing a local git server with authentication.

Copyright:
    2026 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of gitcache (https://github.com/seeraven/gitcache)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""

# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
import logging
import subprocess
import tempfile
from multiprocessing import Process

import uvicorn

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Gitserver Interface
# -----------------------------------------------------------------------------
class GitserverIfc:
    """Provides a simple interface to start, initialize and stop the local git server."""

    def __init__(self) -> None:
        """Initialize the git server process."""
        self._process = Process(target=self._run_gitserver)
        self.remote_url = "http://gitcachetest:passWord@localhost:7698"

    def __enter__(self):
        """Start and initialize the local git server."""
        LOG.debug("Start local gitserver.")
        self._process.start()
        self._process.join(0.5)
        if not self._process.is_alive():
            LOG.error("gitserver process died during startup with exit code %d!", self._process.exitcode)
            raise ChildProcessError()

        LOG.debug("Local git server started.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the local git server."""
        LOG.debug("Stop local gitserver.")
        self._process.terminate()
        self._process.join(2.0)
        if self._process.is_alive():
            LOG.warning("gitserver process did not terminate yet. Let's kill it.")
            self._process.kill()
            self._process.join()
        LOG.debug("gitserver process stopped.")

    def get_localserver_url(self, repo_name: str) -> str:
        """Construct the URL for the repository on the local gitserver."""
        return f"{self.remote_url}/{repo_name}"

    def get_filtered_url(self, repo_name: str) -> str:
        """Construct the URL for the repository without the credentials."""
        return self.get_localserver_url(repo_name).replace("gitcachetest:passWord@", "")

    def initialize(self, remote_url: str, repo_name: str) -> None:
        """Initialize the local gitserver by cloning the specified external
        repository and pushing it to the local server."""
        with tempfile.TemporaryDirectory(prefix="gitserver_init") as tmp_dir:
            LOG.debug("Cloning %s into %s...", remote_url, tmp_dir)
            command = ["git", "clone", remote_url, tmp_dir]
            result = subprocess.run(command, shell=False, check=True)

            if result.returncode != 0:
                LOG.error("Cloning failed with return code %d!", result.returncode)
                raise ChildProcessError()

            tgt_url = self.get_localserver_url(repo_name)
            command = ["git", "-C", tmp_dir, "remote", "set-url", "--push", "origin", tgt_url]
            result = subprocess.run(command, shell=False, check=True)

            if result.returncode != 0:
                LOG.error("Can't set remote URL to %s. Command failed with return code %d!", tgt_url, result.returncode)
                raise ChildProcessError()

            LOG.debug("Pushing from %s to %s...", tmp_dir, tgt_url)
            command = ["git", "-C", tmp_dir, "push", "origin", "master"]
            result = subprocess.run(command, shell=False, check=True)

            if result.returncode != 0:
                LOG.error("Push to local server failed with return code %d!", result.returncode)
                raise ChildProcessError()

    def _run_gitserver(self) -> None:
        """Main function of the process."""
        uvicorn.run("helpers.gitserver:app", port=7698, log_level="info")
