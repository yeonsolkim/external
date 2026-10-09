"""The Realtime TTS path without the network: WebSocket framing, the verbatim check and the
rate limit."""
import struct
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

from _narrator import realtime, tts, wsclient


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

    def test_a_voiced_subscript_is_not_a_misreading(self):
        # The model says "x sub n" where the script, as the lecture prompt asks, says "x n".
        script = "A sequence x n in R is increasing if x n is at most x sub n plus one."
        said = "A sequence x sub n in R is increasing if x sub n is at most x sub n plus one."
        self.assertEqual(realtime.similarity(script, said), 1.0)

    def test_a_symbol_spelled_letter_by_letter_is_one_word(self):
        # The script spells \operatorname{cl} "c l"; the transcript may run the letters together.
        script = "Since c l is extensive, S is contained in c l of S, so c l of S equals S; c l is idempotent."
        for said in ("Since CL is extensive, S is contained in CL of S, so CL of S equals S; CL is idempotent.",
                     "Since C-L is extensive, S is contained in C L of S, so cl of S equals S; C L is idempotent."):
            self.assertEqual(realtime.similarity(script, said), 1.0)
        # Saying the concept for the symbol is still a misreading.
        self.assertLess(realtime.similarity(script, "Since closure is extensive, S is contained in the "
                                                    "closure of S, so the closure of S equals S."),
                        realtime.VERBATIM_RATIO)

    def test_an_answer_is_not_a_reading(self):
        script = "Exchanges provide forums where traders meet to arrange trades."
        self.assertLess(realtime.similarity(script, "Sure! Exchanges are places where people trade."),
                        realtime.VERBATIM_RATIO)
        self.assertLess(realtime.similarity(script, script + " Would you like to know more about exchanges?"),
                        realtime.VERBATIM_RATIO)


LIMITED = {"type": "error", "error": {"message": (
    "Rate limit reached for gpt-realtime-2.1-mini (for limit gpt-4o-mini-realtime) in organization "
    "org-x on tokens per min (TPM): Limit 40000, Used 40000, Requested 1. Please try again in 1ms.")}}


class RateLimit(unittest.TestCase):
    def synth(self, once):
        """synth() over a fake call, with the waits recorded instead of slept."""
        with mock.patch.object(realtime, "_once", once), mock.patch.object(realtime, "time") as clock, \
                mock.patch.object(realtime, "random") as rnd:
            rnd.uniform.return_value = 1.0
            try:
                return realtime.synth("Read this.", "cedar", "gpt-realtime-2.1-mini")
            finally:
                self.waits = [c.args[0] for c in clock.sleep.call_args_list]

    def test_a_rate_limit_is_told_from_other_errors(self):
        self.assertIsInstance(realtime._failure("m", LIMITED), realtime.RateLimited)
        coded = {"type": "error", "error": {"code": "rate_limit_exceeded", "message": "Slow down."}}
        self.assertIsInstance(realtime._failure("m", coded), realtime.RateLimited)
        other = realtime._failure("m", {"type": "error", "error": {"message": "Invalid voice."}})
        self.assertIsInstance(other, tts.TTSError)
        self.assertNotIsInstance(other, realtime.RateLimited)

    def test_a_rate_limit_is_waited_out_and_is_not_a_reading_attempt(self):
        calls = []

        def once(text, *_):
            calls.append(text)
            if len(calls) <= realtime.ATTEMPTS:
                raise realtime._failure("m", LIMITED)
            return b"\x00\x01" * 8, text, {}

        self.assertEqual(self.synth(once), b"\x00\x01" * 8)
        self.assertEqual(len(calls), realtime.ATTEMPTS + 1)
        self.assertEqual(self.waits, [5.0, 10.0, 20.0])

    def test_a_rate_limit_that_does_not_lift_is_an_error(self):
        def once(text, *_):
            raise realtime._failure("m", LIMITED)

        with self.assertRaises(realtime.RateLimited):
            self.synth(once)
        self.assertEqual(len(self.waits), realtime.RATE_LIMIT_RETRIES)
        self.assertEqual(max(self.waits), 60.0)

    def test_at_most_max_sessions_calls_run_at_once(self):
        lock, running, peak = threading.Lock(), [0], [0]

        def once(text, *_):
            with lock:
                running[0] += 1
                peak[0] = max(peak[0], running[0])
            time.sleep(0.02)
            with lock:
                running[0] -= 1
            return b"\x00\x01", text, {}

        with mock.patch.object(realtime, "_once", once):
            with ThreadPoolExecutor(max_workers=2 * realtime.MAX_SESSIONS) as pool:
                list(pool.map(lambda i: realtime.synth("Read %d." % i, "cedar", "m"),
                              range(4 * realtime.MAX_SESSIONS)))
        self.assertLessEqual(peak[0], realtime.MAX_SESSIONS)


if __name__ == "__main__":
    unittest.main()
