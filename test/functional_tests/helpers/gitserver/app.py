"""
Module implementing the git server for uvicorn.
"""

import secrets
import tempfile
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.requests import Request
from starlette.responses import StreamingResponse

from .git import Git

# pylint: disable=consider-using-with
TEMPDIR = tempfile.TemporaryDirectory(prefix="gitserver_")
USERNAME = "gitcachetest"
PASSWORD = "passWord"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Custom lifespan model for FastAPI to provide a cleanup."""
    yield
    TEMPDIR.cleanup()


app = FastAPI(lifespan=lifespan)
security = HTTPBasic()


class Service(Enum):
    """Enum collecting the git services."""

    RECEIVE = "git-receive-pack"
    UPLOAD = "git-upload-pack"


def auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:  # noqa
    """Simple authentication to allow only the hard-coded user."""
    username = secrets.compare_digest(credentials.username, USERNAME)
    password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (username and password):
        raise HTTPException(status_code=401)
    return credentials.username


@app.get("/{path}/info/refs")
# pylint: disable=redefined-outer-name
async def info(path: str, service: Service, _user: str = Depends(auth)):  # noqa
    """Handle access of the /info/refs URL."""
    full_path = Path(TEMPDIR.name, path)

    # Create repo if does does not exist
    repo = Git(full_path) if full_path.exists() else Git.init(full_path)

    # Fetch inforefs
    data = repo.inforefs(service.value)

    media = f"application/x-{service.value}-advertisement"
    return StreamingResponse(data, media_type=media)


@app.post("/{path}/{service}")
# pylint: disable=redefined-outer-name
async def service(path: str, service: Service, req: Request):
    """Handle access to a service."""
    full_path = Path(TEMPDIR.name, path)
    repo = Git(full_path)

    # Load data to memory (be careful with huge repos)
    stream = req.stream()
    data_list = [data async for data in stream]
    data = b"".join(data_list)

    # Load service data
    data_io = repo.service(service.value, data)

    media = f"application/x-{service.value}-result"
    return StreamingResponse(data_io, media_type=media)
