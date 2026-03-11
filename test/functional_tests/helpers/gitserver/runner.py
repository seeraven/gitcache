"""
Module replacing the Runner class to make it compatible with Windows.
"""

import subprocess
from subprocess import PIPE, CompletedProcess, Popen
from typing import Any, Dict, List, Optional


class Runner:
    """Execution of commands."""

    PIPE = PIPE

    def __init__(self, command: str):
        self._args: List[str] = []
        self._env: Optional[Dict[str, str]] = None

        self.arg(command)  # type: ignore

    def arg(self, *args: Any) -> "Runner":
        """Add an argument or a list of arguments."""
        args_as_str = [str(a) for a in args]
        self._args.extend(args_as_str)
        return self

    def env(self, **kwargs: Any) -> "Runner":
        """Update the environment."""
        self._env = self._env or {}
        kwargs_as_str = {k: str(v) for k, v in kwargs.items()}
        self._env.update(kwargs_as_str)
        return self

    def run(self, *args: Any, **kwargs: Any) -> CompletedProcess:
        """Run the command."""
        # pylint: disable=subprocess-run-check
        return subprocess.run(self._args, *args, env=self._env, **kwargs)  # type: ignore

    def popen(self, *args: Any, **kwargs: Any) -> Popen:
        """Execute the command in a popen call."""
        return subprocess.Popen(self._args, *args, env=self._env, **kwargs)  # type: ignore
