#!/usr/bin/env python3
"""Campus Notice Board API (CTE412 Practical 6).

One source tree, three images. Behaviour is selected at build time by
APP_VERSION / BROKEN, and at run time by FEATURE_PINNED:

  1.0.0         baseline
  1.1.0         adds category + pinned fields, FEATURE_PINNED ordering
  1.2.0-broken  identical to 1.1.0 but /healthz never returns 200

Standard library only, so the Alpine image stays small.
"""
import json
import os
import re
import signal
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

START = time.monotonic()                       # process start, for the warm-up window
VERSION = os.environ.get("APP_VERSION", "1.0.0")
STUDENT = os.environ.get("STUDENT_ID", "02230137")
BROKEN = os.environ.get("BROKEN", "false").strip().lower() == "true"
FEATURE_PINNED = os.environ.get("FEATURE_PINNED", "false").strip().lower() == "true"
WARMUP_SECONDS = 5.0                           # /healthz is unhealthy for this long
PORT = 8080
POD = socket.gethostname()                     # the Pod name inside Kubernetes

# 1.1.0 and later carry the extra fields. "1.2.0-broken" parses as 1.2.
_m = re.match(r"(\d+)\.(\d+)", VERSION)
ENHANCED = bool(_m) and (int(_m.group(1)), int(_m.group(2))) >= (1, 1)

NOTICES = [
    {"id": 1, "title": "Library opens until 22:00 during examinations",
     "body": "Extended hours run from Monday to Friday.",
     "category": "Library", "pinned": False},
    {"id": 2, "title": "Semester examination timetable published",
     "body": "Check the Academic Section board for your programme.",
     "category": "Academic", "pinned": True},
    {"id": 3, "title": "Hostel fee payment deadline",
     "body": "Payments after the deadline attract a late fee.",
     "category": "Finance", "pinned": False},
    {"id": 4, "title": "Career fair registration open",
     "body": "Register at the Student Services Office.",
     "category": "Career", "pinned": False},
]


def notices_payload():
    if not ENHANCED:                           # baseline: id, title, body only
        return {"notices": [{k: n[k] for k in ("id", "title", "body")} for n in NOTICES]}
    items = [dict(n) for n in NOTICES]
    if FEATURE_PINNED:
        items.sort(key=lambda n: not n["pinned"])   # stable: pinned first, rest unchanged
    return {"pinnedFirst": FEATURE_PINNED, "notices": items}


def healthy():
    return (not BROKEN) and (time.monotonic() - START) >= WARMUP_SECONDS


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/notices":
            self._send(200, notices_payload())
        elif path == "/version":
            # Key order matters: the monitor and summariser parse "version" first.
            self._send(200, {"version": VERSION, "student": STUDENT, "pod": POD})
        elif path == "/healthz":
            if healthy():
                self._send(200, {"status": "ok"})
            else:
                self._send(503, {"status": "unhealthy"})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, fmt, *args):         # probes would flood the log
        pass


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)

    def stop(signum, frame):                   # PID 1 ignores SIGTERM unless handled
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    print(f"notice-board {VERSION} student={STUDENT} pod={POD} "
          f"broken={BROKEN} pinned={FEATURE_PINNED} port={PORT}", flush=True)
    server.serve_forever()
    server.server_close()


if __name__ == "__main__":
    main()
