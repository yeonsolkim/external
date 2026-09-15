"""SigV4 pinned to the vector AWS publishes for GET Object with a Range header."""
import datetime as dt
import unittest

from _narrator.store import Store, uri_encode


class SigV4(unittest.TestCase):
    def test_aws_published_vector(self):
        store = Store("https://s3.amazonaws.com", "examplebucket", "AKIAIOSFODNN7EXAMPLE",
                      "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", region="us-east-1", path_style=False)
        when = dt.datetime(2013, 5, 24, tzinfo=dt.timezone.utc)
        url, headers = store.sign("GET", "test.txt", {"range": "bytes=0-9"}, b"", now=when)
        self.assertEqual(url, "https://examplebucket.s3.amazonaws.com/test.txt")
        self.assertEqual(
            headers["authorization"],
            "AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20130524/us-east-1/s3/aws4_request,"
            "SignedHeaders=host;range;x-amz-content-sha256;x-amz-date,"
            "Signature=f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41")

    def test_path_style_and_prefix(self):
        store = Store("https://abc.r2.cloudflarestorage.com", "audio", "k", "s", prefix="ext/")
        url, _ = store.sign("PUT", "2026/07/30/a b.mp3", {}, b"x")
        self.assertEqual(url, "https://abc.r2.cloudflarestorage.com/audio/ext/2026/07/30/a%20b.mp3")

    def test_uri_encode(self):
        self.assertEqual(uri_encode("a b+c/é", False), "a%20b%2Bc/%C3%A9")
        self.assertEqual(uri_encode("a/b"), "a%2Fb")


if __name__ == "__main__":
    unittest.main()
