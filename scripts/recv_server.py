#!/usr/bin/env python3
"""Tiny localhost receiver: POST /save?name=X writes body to ~/Downloads/X.txt"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import re

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        q = parse_qs(urlparse(self.path).query)
        name = re.sub(r"[^\w-]", "", q.get("name", ["x"])[0])
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        (Path.home() / "Downloads" / f"{name}.txt").write_bytes(body)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"ok")
        print(f"saved {name} ({len(body)} bytes)", flush=True)

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        name = re.sub(r"[^\w-]", "", q.get("name", ["x"])[0])
        data = q.get("data", [""])[0]
        if data:
            (Path.home() / "Downloads" / f"{name}.txt").write_text(data, encoding="utf-8")
            print(f"saved {name} ({len(data)} chars)", flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"ok {name} {len(data)}".encode())

    def log_message(self, *a):
        pass

HTTPServer(("127.0.0.1", 8765), H).serve_forever()
