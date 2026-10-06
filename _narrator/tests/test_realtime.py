"""The Realtime TTS path without the network: WebSocket framing and the verbatim check."""
import struct
import unittest

from _narrator import realtime, wsclient


class FakeSocket:
    def __init__(self, incoming: bytes) -> None:
        self.incoming = incoming
        self.sent = b""

    def recv(self, n: int) -> bytes:
        out, self.incoming = self.incoming[:n], self.incoming[n:]
        return out

    def sendall(self, data: bytes) -> None:
        self.sent += data

    def close(self) -> None:
        pass


def frame(opcode: int, payload: bytes, fin: bool = True) -> bytes:
    """A server frame: unmasked, as RFC 6455 requires of servers."""
    first = (0x80 if fin else 0) | opcode
    if len(payload) < 126:
        return struct.pack("!BB", first, len(payload)) + payload
    return struct.pack("!BBH", first, 126, len(payload)) + payload


def client(incoming: bytes) -> wsclient.WebSocket:
    ws = object.__new__(wsclient.WebSocket)
    ws.sock, ws.closed, ws._buf = FakeSocket(incoming), False, b""
    return ws


class Framing(unittest.TestCase):
    def test_mask_is_an_involution(self):
        data, key = b"hello, realtime" * 50, b"\x01\x80\xfe\x7f"
        self.assertEqual(wsclient._mask(wsclient._mask(data, key), key), data)

    def test_fragments_pings_and_long_frames(self):
        long = b'{"delta":"' + b"A" * 300 + b'"}'
        ws = client(frame(wsclient.TEXT, b'{"type":', fin=False) + frame(wsclient.PING, b"p")
                    + frame(0x0, b'"x"}') + frame(wsclient.TEXT, long) + frame(wsclient.CLOSE, b"\x03\xe8"))
        self.assertEqual(ws.recv_json(), {"type": "x"})
        self.assertEqual(ws.recv(), long.decode())
        self.assertIsNone(ws.recv())
        sent = ws.sock.sent
        self.assertEqual(sent[0], 0x80 | wsclient.PONG)       # the ping was answered
        self.assertTrue(sent[1] & 0x80)                         # client frames are masked

    def test_client_frame_round_trips(self):
        ws = client(b"")
        ws.send_json({"type": "response.create"})
        raw = ws.sock.sent
        n = raw[1] & 0x7F
        self.assertEqual(wsclient._mask(raw[6:6 + n], raw[2:6]), b'{"type": "response.create"}')


class Verbatim(unittest.TestCase):
    def test_numbers_and_labels_compare_equal(self):
        self.assertEqual(realtime.similarity("1 point 1 point 1 Traders.", "1.1.1 traders"), 1.0)
        self.assertEqual(realtime.similarity("sixty percent of 10 thousand", "60% of ten thousand"), 1.0)

    def test_an_answer_is_not_a_reading(self):
        script = "Exchanges provide forums where traders meet to arrange trades."
        self.assertLess(realtime.similarity(script, "Sure! Exchanges are places where people trade."),
                        realtime.VERBATIM_RATIO)
        self.assertLess(realtime.similarity(script, script + " Would you like to know more about exchanges?"),
                        realtime.VERBATIM_RATIO)


if __name__ == "__main__":
    unittest.main()
