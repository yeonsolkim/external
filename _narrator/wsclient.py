"""A minimal WebSocket client (RFC 6455) on the standard library — what the Realtime API
needs and nothing more: one TLS connection, JSON text frames both ways, ping/pong, close.
No extensions (no permessage-deflate), so frames arrive as plain bytes."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import ssl
import struct
from typing import Optional
from urllib.parse import urlsplit

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
TEXT, BINARY, CLOSE, PING, PONG = 0x1, 0x2, 0x8, 0x9, 0xA


class WebSocketError(Exception):
    pass


def _mask(data: bytes, key: bytes) -> bytes:
    if not data:
        return data
    pad = (key * (len(data) // 4 + 1))[:len(data)]
    return (int.from_bytes(data, "big") ^ int.from_bytes(pad, "big")).to_bytes(len(data), "big")


class WebSocket:
    def __init__(self, url: str, headers: Optional[dict] = None, timeout: float = 60.0) -> None:
        parts = urlsplit(url)
        if parts.scheme not in ("ws", "wss"):
            raise WebSocketError("not a WebSocket URL: %s" % url)
        host = parts.hostname or ""
        port = parts.port or (443 if parts.scheme == "wss" else 80)
        path = (parts.path or "/") + ("?" + parts.query if parts.query else "")
        sock = socket.create_connection((host, port), timeout=timeout)
        if parts.scheme == "wss":
            sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host)
        self.sock = sock
        self.closed = False
        self._buf = b""

        key = base64.b64encode(os.urandom(16)).decode("ascii")
        lines = ["GET %s HTTP/1.1" % path, "Host: %s" % host, "Upgrade: websocket",
                 "Connection: Upgrade", "Sec-WebSocket-Key: " + key, "Sec-WebSocket-Version: 13"]
        lines += ["%s: %s" % item for item in (headers or {}).items()]
        self.sock.sendall(("\r\n".join(lines) + "\r\n\r\n").encode("latin-1"))

        head = self._read_until(b"\r\n\r\n").decode("latin-1").split("\r\n")
        try:
            status = int(head[0].split()[1])
        except (IndexError, ValueError):
            raise WebSocketError("bad handshake response: %r" % head[0])
        found = {}
        for line in head[1:]:
            if ":" in line:
                name, value = line.split(":", 1)
                found[name.strip().lower()] = value.strip()
        if status != 101:
            body = self._buf
            length = int(found.get("content-length", "0") or 0)
            try:
                while len(body) < length:
                    chunk = self.sock.recv(65536)
                    if not chunk:
                        break
                    body += chunk
            except OSError:
                pass
            self.sock.close()
            raise WebSocketError("handshake %d: %s" % (status, body[:400].decode("utf-8", "replace")))
        expect = base64.b64encode(hashlib.sha1((key + GUID).encode("ascii")).digest()).decode("ascii")
        if found.get("sec-websocket-accept") != expect:
            self.sock.close()
            raise WebSocketError("handshake: wrong Sec-WebSocket-Accept")

    # bytes ---------------------------------------------------------------------
    def _fill(self) -> None:
        chunk = self.sock.recv(65536)
        if not chunk:
            self.closed = True
            raise WebSocketError("connection closed by the server")
        self._buf += chunk

    def _read_until(self, marker: bytes) -> bytes:
        while marker not in self._buf:
            self._fill()
        head, self._buf = self._buf.split(marker, 1)
        return head

    def _read(self, n: int) -> bytes:
        while len(self._buf) < n:
            self._fill()
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    # frames --------------------------------------------------------------------
    def _send_frame(self, opcode: int, payload: bytes) -> None:
        n = len(payload)
        if n < 126:
            header = struct.pack("!BB", 0x80 | opcode, 0x80 | n)
        elif n < 65536:
            header = struct.pack("!BBH", 0x80 | opcode, 0x80 | 126, n)
        else:
            header = struct.pack("!BBQ", 0x80 | opcode, 0x80 | 127, n)
        key = os.urandom(4)
        self.sock.sendall(header + key + _mask(payload, key))

    def send_json(self, event: dict) -> None:
        self._send_frame(TEXT, json.dumps(event).encode("utf-8"))

    def recv(self) -> Optional[str]:
        """The next text message; None once the server closes."""
        parts = []
        while True:
            first, second = self._read(2)
            fin, opcode = first & 0x80, first & 0x0F
            n = second & 0x7F
            if n == 126:
                n = struct.unpack("!H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack("!Q", self._read(8))[0]
            key = self._read(4) if second & 0x80 else b""
            payload = self._read(n)
            if key:
                payload = _mask(payload, key)
            if opcode == PING:
                self._send_frame(PONG, payload)
                continue
            if opcode == PONG:
                continue
            if opcode == CLOSE:
                self.close()
                return None
            parts.append(payload)
            if fin:
                return b"".join(parts).decode("utf-8")

    def recv_json(self) -> Optional[dict]:
        message = self.recv()
        return None if message is None else json.loads(message)

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            try:
                self._send_frame(CLOSE, struct.pack("!H", 1000))
            except OSError:
                pass
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self) -> "WebSocket":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
