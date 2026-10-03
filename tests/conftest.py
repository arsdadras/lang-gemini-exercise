"""Fixtures shared across test modules."""

import socket
from collections.abc import Iterator

import pytest


@pytest.fixture
def silent_server() -> Iterator[str]:
    """A local address that accepts connections and never answers, so every read times out."""
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(4)
    yield f"http://127.0.0.1:{server.getsockname()[1]}"
    server.close()


@pytest.fixture
def closed_port() -> str:
    """A local address nothing listens on, so every connection is refused."""
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return f"http://127.0.0.1:{port}"
