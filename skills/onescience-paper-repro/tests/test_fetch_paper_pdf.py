"""Behavioral regression for binary download, cache preservation and bad responses."""

from contextlib import redirect_stdout
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import build_opener, ProxyHandler


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fetch_paper_pdf.py"
SPEC = importlib.util.spec_from_file_location("fetch_paper_pdf", SCRIPT)
fetcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetcher)


def pdf_fixture():
    # A valid one-page PDF, padded with comments to exceed the host's 5MB limit.
    data = bytearray(b"%PDF-1.4\n" + b"% padding\n" * 600000)
    offsets = [0]
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] >>",
    ]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(data)
    data.extend(b"xref\n0 4\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(data)


class FetchPDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = pdf_fixture()
        cls.requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                cls.requests.append(self.path)
                if self.path == "/missing":
                    self.send_error(404)
                    return
                if self.path == "/broken_chunked":
                    self.send_response(200)
                    self.send_header("Transfer-Encoding", "chunked")
                    self.end_headers()
                    self.wfile.write(b"10\r\nshort")
                    self.close_connection = True
                    return
                if self.path == "/html":
                    body = b"<html>Rate limit or login page</html>"
                elif self.path == "/cut_pdf":
                    body = cls.payload[:-20]
                else:
                    body = cls.payload
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Length", str(len(body) + (100 if self.path == "/truncated" else 0)))
                self.end_headers()
                self.wfile.write(body)
                self.close_connection = True

            def log_message(self, *args):
                pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "paper.pdf"
        # The cluster may proxy all HTTP, including localhost. Keep regression
        # traffic on the local fixture server; production retains its proxy.
        local_opener = build_opener(ProxyHandler({}))
        mocked = patch.object(fetcher, "urlopen", local_opener.open)
        mocked.start()
        self.addCleanup(mocked.stop)

    def test_large_pdf_and_cache_reuse(self):
        result = fetcher.fetch_pdf(self.base + "/paper", self.output)
        self.assertGreater(result["bytes"], 5 * 1024 * 1024)
        self.assertEqual(self.output.read_bytes(), self.payload)
        self.assertEqual(result["sha256"], hashlib.sha256(self.payload).hexdigest())
        self.assertEqual(result["paper_identity_and_full_text"], "not_checked")
        before = len(self.requests)
        cached = fetcher.fetch_pdf(self.base + "/missing", self.output)
        self.assertEqual(cached["status"], "cached")
        self.assertEqual(len(self.requests), before)
        self.assertEqual(list(self.output.parent.glob("*.part")), [])

    def test_html_is_rejected_despite_pdf_content_type(self):
        with self.assertRaisesRegex(ValueError, "not a PDF"):
            fetcher.fetch_pdf(self.base + "/html", self.output)
        self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_interrupted_transfer_and_incomplete_pdf_leave_no_cache(self):
        for endpoint in ("/truncated", "/cut_pdf"):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises((OSError, ValueError)):
                    fetcher.fetch_pdf(self.base + endpoint, self.output)
                self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_invalid_existing_cache_is_preserved(self):
        self.output.write_bytes(b"existing cache requiring examination")
        before = len(self.requests)
        with self.assertRaises(ValueError):
            fetcher.fetch_pdf(self.base + "/paper", self.output)
        self.assertEqual(len(self.requests), before)
        self.assertEqual(self.output.read_bytes(), b"existing cache requiring examination")

    def test_cli_http_error_is_compact_and_nonzero(self):
        output = io.StringIO()
        with patch("sys.argv", [str(SCRIPT), "--url", self.base + "/missing", "--output", str(self.output)]):
            with redirect_stdout(output):
                code = fetcher.main()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "failed")
        self.assertLess(len(output.getvalue()), 1200)
        self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_cli_broken_chunked_transfer_is_nonzero_without_partial_cache(self):
        output = io.StringIO()
        with patch("sys.argv", [str(SCRIPT), "--url", self.base + "/broken_chunked", "--output", str(self.output)]):
            with redirect_stdout(output):
                code = fetcher.main()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "failed")
        self.assertEqual(list(self.output.parent.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
