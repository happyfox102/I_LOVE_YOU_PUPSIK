import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from database import get_last_signature, init_db, save_signature


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"
HOST = "127.0.0.1"
PORT = 8000


class ValentineHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_index(self) -> None:
        if not INDEX_FILE.exists():
            self.send_error(404, "index.html not found")
            return
        body = INDEX_FILE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._serve_index()
            return
        if parsed.path == "/api/last":
            last = get_last_signature()
            self._send_json({"ok": True, "last": last})
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/sign":
            self.send_error(404, "Not found")
            return

        length_header = self.headers.get("Content-Length", "0")
        try:
            raw_length = int(length_header)
        except ValueError:
            self._send_json({"ok": False, "error": "Bad Content-Length"}, 400)
            return

        raw_data = self.rfile.read(raw_length)
        try:
            payload = json.loads(raw_data.decode("utf-8")) if raw_data else {}
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return

        hold_seconds = float(payload.get("holdSeconds", 0))
        note = payload.get("note")
        if hold_seconds < 5:
            self._send_json(
                {"ok": False, "error": "Hold duration must be at least 5 seconds"},
                400,
            )
            return

        doc_id = save_signature(hold_seconds=hold_seconds, note=note)
        last = get_last_signature()
        self._send_json({"ok": True, "documentId": doc_id, "document": last})

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> None:
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), ValentineHandler)
    print(f"Valentine server running on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()