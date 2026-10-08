from __future__ import annotations

import asyncio
import logging
import sys

from .server import create_server

logging.basicConfig(level=logging.INFO, stream=sys.stderr)


def main() -> None:
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
