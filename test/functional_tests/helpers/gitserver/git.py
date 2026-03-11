"""
Module providing the Git class.
"""

from __future__ import annotations

import io

# import stat
from pathlib import Path
from subprocess import PIPE
from typing import IO

from .runner import Runner


class Git:
    """Representation of the git service."""

    def __init__(self, path: Path):
        self.path = Path(path)

    @staticmethod
    def init(path: Path) -> Git:
        """Initialize a bare git repository."""
        Runner("git").arg("init").arg("--bare").arg(path).run(check=True)
        return Git(path)

    # def add_hook(self, name: str, hook: str) -> str:
    #     """Add a hook to the git repository."""
    #     path = Path(self.path, "hooks", name)
    #     path.write_text(hook)
    #     st = path.stat()
    #     path.chmod(st.st_mode | stat.S_IEXEC)
    #     return str(path)

    def inforefs(self, service: str) -> IO:
        """Get the data for the /info/refs point."""
        result = (
            Runner(service)
            .arg("--stateless-rpc")
            .arg("--advertise-refs")
            .arg(self.path)
            .run(check=True, capture_output=True)
        )

        # Adapted from:
        #   https://github.com/schacon/grack/blob/master/lib/grack.rb
        data = b"# service=" + service.encode()
        datalen = len(data) + 4
        datalen_encoded = b"%04x" % datalen
        data = datalen_encoded + data + b"0000" + result.stdout

        return io.BytesIO(data)

    def service(self, service: str, data: bytes) -> IO:
        """Handle the access to the git service."""
        proc = Runner(service).arg("--stateless-rpc").arg(self.path).popen(stdin=PIPE, stdout=PIPE)

        try:
            data, _ = proc.communicate(data)
        finally:
            proc.wait()

        return io.BytesIO(data)
