#!/usr/bin/env python3
"""Make one simple TCP echo request to the W6300 server."""

import argparse
import socket
import sys

DEFAULT_HOST = "192.168.0.10"
DEFAULT_PORT = 5000
DEFAULT_TIMEOUT = 5.0
DEFAULT_MESSAGE = "W6300 TCP echo test"


def recv_exact(connection: socket.socket, size: int) -> bytes:
    """Receive exactly size bytes; TCP may return only part of the data."""
    received = bytearray()
    while len(received) < size:
        chunk = connection.recv(size - len(received))
        if not chunk:
            raise ConnectionError(
                f"server closed after {len(received)} of {size} expected bytes"
            )
        received.extend(chunk)
    return bytes(received)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST, help="server IPv4 address")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="server TCP port")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="timeout in seconds")
    parser.add_argument("--message", default=DEFAULT_MESSAGE, help="UTF-8 text to send")
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    payload = args.message.encode("utf-8")
    try:
        with socket.create_connection((args.host, args.port), timeout=args.timeout) as connection:
            connection.settimeout(args.timeout)
            connection.sendall(payload)
            echoed = recv_exact(connection, len(payload))

        if echoed != payload:
            print(f"FAIL: sent {payload!r}, received {echoed!r}", file=sys.stderr)
            return 1

        print(f"PASS: {args.host}:{args.port} echoed {echoed!r}")
        return 0
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130
    except (OSError, ConnectionError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())