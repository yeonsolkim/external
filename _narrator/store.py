"""
Minimal S3-compatible object store client (Cloudflare R2, AWS S3, MinIO…): SigV4 in the
Authorization header, urllib, no SDK. Ported from the Legato backend's s3.mjs and pinned
to AWS's published signing vector in tests/test_store.py.

Configuration (environment or .env):
    S3_ENDPOINT            https://<account>.r2.cloudflarestorage.com
    S3_BUCKET              bucket name
    S3_ACCESS_KEY_ID / S3_SECRET_ACCESS_KEY
    S3_REGION              "auto" for R2 (default)
    S3_PREFIX              optional key prefix, e.g. "external/"
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import hmac
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from .env import require


class StoreError(Exception):
    pass


def _sha256hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hmac(key: bytes, data: str) -> bytes:
    return hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()


def uri_encode(text: str, encode_slash: bool = True) -> str:
    out = []
    for byte in text.encode("utf-8"):
        ch = chr(byte)
        if ch.isalnum() and byte < 128 or ch in "-._~":
            out.append(ch)
        elif ch == "/":
            out.append("%2F" if encode_slash else "/")
        else:
            out.append("%%%02X" % byte)
    return "".join(out)


class Store:
    def __init__(self, endpoint: str, bucket: str, access_key: str, secret_key: str,
                 region: str = "auto", prefix: str = "", path_style: bool = True) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.prefix = prefix
        self.path_style = path_style
        parsed = urllib.parse.urlsplit(self.endpoint)
        self._scheme, self._host, self._base_path = parsed.scheme, parsed.netloc, parsed.path.rstrip("/")

    @classmethod
    def from_env(cls) -> "Store":
        return cls(require("S3_ENDPOINT"), require("S3_BUCKET"), require("S3_ACCESS_KEY_ID"),
                   require("S3_SECRET_ACCESS_KEY"), os.environ.get("S3_REGION", "auto") or "auto",
                   os.environ.get("S3_PREFIX", ""))

    # -- signing ---------------------------------------------------------------
    def _target(self, key: str) -> tuple:
        encoded = uri_encode(self.prefix + key, encode_slash=False)
        if self.path_style:
            path = "%s/%s/%s" % (self._base_path, self.bucket, encoded)
            return "%s://%s%s" % (self._scheme, self._host, path), self._host, path
        host = "%s.%s" % (self.bucket, self._host)
        path = "/" + encoded
        return "%s://%s%s" % (self._scheme, host, path), host, path

    def sign(self, method: str, key: str, headers: Optional[dict] = None, body: bytes = b"",
             now: Optional[_dt.datetime] = None) -> tuple:
        """-> (url, headers) with the Authorization header added."""
        now = now or _dt.datetime.now(_dt.timezone.utc)
        amz = now.strftime("%Y%m%dT%H%M%SZ")
        stamp = amz[:8]
        url, host, path = self._target(key)
        payload = _sha256hex(body)
        h = dict(headers or {})
        h.update({"host": host, "x-amz-content-sha256": payload, "x-amz-date": amz})
        names = sorted(k.lower() for k in h)
        lookup = {k.lower(): v for k, v in h.items()}
        canonical_headers = "".join("%s:%s\n" % (n, " ".join(str(lookup[n]).split())) for n in names)
        signed = ";".join(names)
        canonical = "\n".join([method, path, "", canonical_headers, signed, payload])
        scope = "%s/%s/s3/aws4_request" % (stamp, self.region)
        to_sign = "\n".join(["AWS4-HMAC-SHA256", amz, scope, _sha256hex(canonical.encode("utf-8"))])
        k = _hmac(("AWS4" + self.secret_key).encode("utf-8"), stamp)
        k = _hmac(_hmac(_hmac(k, self.region), "s3"), "aws4_request")
        signature = hmac.new(k, to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        h["authorization"] = "AWS4-HMAC-SHA256 Credential=%s/%s,SignedHeaders=%s,Signature=%s" % (
            self.access_key, scope, signed, signature)
        del h["host"]           # urllib sets it; signing it was what mattered
        return url, h

    # -- operations ------------------------------------------------------------
    def _send(self, method: str, key: str, headers: Optional[dict] = None, body: bytes = b"",
              timeout: int = 300):
        url, h = self.sign(method, key, headers, body)
        request = urllib.request.Request(url, data=body if method in ("PUT", "POST") else None,
                                         method=method, headers=h)
        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            raise StoreError("%s %s -> %s %s" % (method, key, error.code,
                                                 error.read().decode("utf-8", "replace")[:300]))
        except urllib.error.URLError as error:
            raise StoreError("%s %s -> %s" % (method, key, error))

    def put(self, key: str, body: bytes, content_type: str, cache_control: str = "") -> None:
        headers = {"content-type": content_type, "content-length": str(len(body))}
        if cache_control:
            headers["cache-control"] = cache_control
        response = self._send("PUT", key, headers, body)
        if response is None:
            raise StoreError("PUT %s -> 404 (bucket missing?)" % key)
        response.close()

    def put_file(self, key: str, path: str, content_type: str, cache_control: str = "") -> None:
        with open(path, "rb") as handle:
            self.put(key, handle.read(), content_type, cache_control)

    def get(self, key: str) -> Optional[bytes]:
        response = self._send("GET", key)
        if response is None:
            return None
        with response:
            return response.read()

    def head(self, key: str) -> Optional[dict]:
        response = self._send("HEAD", key)
        if response is None:
            return None
        with response:
            return {"size": int(response.headers.get("content-length") or 0),
                    "etag": (response.headers.get("etag") or "").strip('"')}

    def copy(self, src_key: str, dst_key: str, content_type: str, cache_control: str = "") -> None:
        """Server-side copy (CopyObject) — re-points a stable alias without re-uploading."""
        headers = {"x-amz-copy-source": "/%s/%s" % (self.bucket, uri_encode(self.prefix + src_key, False)),
                   "x-amz-metadata-directive": "REPLACE", "content-type": content_type}
        if cache_control:
            headers["cache-control"] = cache_control
        response = self._send("PUT", key=dst_key, headers=headers, body=b"")
        if response is None:
            raise StoreError("COPY %s -> %s: source missing" % (src_key, dst_key))
        response.close()

    def delete(self, key: str) -> None:
        response = self._send("DELETE", key)
        if response is not None:
            response.close()
