#!/usr/bin/env python3
"""Stream a selected official PDF to disk without returning its body to the agent.

This checks transport and PDF envelope only. The caller must still verify paper
identity, version, readable pages and full-text coverage with a PDF parser.
"""

import argparse
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def inspect_pdf(path):
    """Return a compact binary-cache summary; do not claim semantic validity."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        header = stream.read(1024)
        if not header.lstrip().startswith(b"%PDF-"):
            raise ValueError("Response is not a PDF (missing PDF header)")
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(max(0, size - 2048))
        if b"%%EOF" not in stream.read():
            raise ValueError("PDF is incomplete (missing end marker)")
        stream.seek(0)
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return {
        "path": str(path.resolve()),
        "bytes": size,
        "sha256": digest.hexdigest(),
        "binary_check": "passed",
        "paper_identity_and_full_text": "not_checked",
    }


def fetch_pdf(url, output, timeout=60):
    if urlparse(url).scheme not in {"http", "https"}:
        raise ValueError("Use an HTTP(S) PDF URL verified by the caller")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    output = Path(output)
    # Reuse without network or overwriting. An invalid existing cache is reported
    # for the caller to examine instead of being silently replaced.
    if output.exists():
        return {"status": "cached", **inspect_pdf(output)}
    output.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (paper-repro PDF acquisition)",
        "Accept": "application/pdf",
        "Accept-Encoding": "identity",
    })
    part = None
    try:
        with urlopen(request, timeout=timeout) as response:
            if urlparse(response.geturl()).scheme not in {"http", "https"}:
                raise ValueError("Unexpected redirect scheme")
            if response.status != 200:
                raise ValueError(f"Expected HTTP 200, got {response.status}")
            length = response.headers.get("Content-Length")
            expected = int(length) if length is not None else None
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=output.parent, prefix=output.name + ".", suffix=".part",
                delete=False,
            ) as stream:
                part = Path(stream.name)
                received = 0
                while True:
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    stream.write(chunk)
                    received += len(chunk)
            if expected is not None and received != expected:
                raise ValueError(f"Incomplete transfer: {received}/{expected} bytes")
            final_url = response.geturl()
        summary = inspect_pdf(part)
        # Publish atomically without clobbering a cache created during download.
        os.link(part, output)
        summary["path"] = str(output.resolve())
        return {"status": "downloaded", "final_url": final_url, **summary}
    finally:
        if part is not None:
            part.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    try:
        result = fetch_pdf(args.url, args.output, args.timeout)
    except (OSError, ValueError, HTTPException) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)[:1000]}))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
