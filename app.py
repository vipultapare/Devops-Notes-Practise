"""DevOps Practice Web Application.

Provides backend functionality (greeting, calculations, and server status)
and serves the web frontend. Supports Flask with a built-in standard library
HTTP server fallback if Flask is not installed.
"""

import json
import os
import platform
import sys
from datetime import datetime

# Core functional logic (preserved & expanded from initial version)
def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def greet(name: str) -> str:
    """Return a personalized greeting message."""
    cleaned = name.strip() if name else "DevOps Engineer"
    return f"Hello, {cleaned}! Welcome to DevOps Practice."


# Check for Flask availability
try:
    from flask import Flask, jsonify, request, send_from_directory
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


if HAS_FLASK:
    # Initialize Flask app
    app = Flask(__name__, static_folder=".", static_url_path="")

    @app.route("/")
    def index():
        """Serve the index.html page."""
        return send_from_directory(".", "index.html")

    @app.route("/api/greet", methods=["POST"])
    def api_greet():
        """Endpoint to generate greeting from Python backend."""
        data = request.get_json(silent=True) or {}
        name = data.get("name", "")
        return jsonify({"message": greet(name)})

    @app.route("/api/add", methods=["POST"])
    def api_add():
        """Endpoint to perform addition via Python backend."""
        data = request.get_json(silent=True) or {}
        try:
            a = float(data.get("a", 0))
            b = float(data.get("b", 0))
            result = add(a, b)
            formatted_result = int(result) if result.is_integer() else result
            return jsonify({
                "result": formatted_result,
                "expression": f"{a} + {b} = {formatted_result}",
            })
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid numbers provided"}), 400

    @app.route("/api/status", methods=["GET"])
    def api_status():
        """Endpoint returning server status and deployment environment details."""
        return jsonify({
            "status": "online",
            "server": "Flask",
            "python_version": sys.version.split()[0],
            "system": platform.system(),
            "platform": platform.platform(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    def run_server(port: int = 5000):
        """Run the Flask web server."""
        print(f"[*] Starting Flask server on http://0.0.0.0:{port}")
        app.run(host="0.0.0.0", port=port, debug=False)

else:
    # Standard library fallback using built-in http.server
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse

    class StandaloneHandler(BaseHTTPRequestHandler):
        """HTTP handler replicating Flask API behavior using built-in modules."""

        def _send_json(self, status_code: int, data: dict):
            payload = json.dumps(data).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                try:
                    with open("index.html", "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_error(404, "index.html not found")
            elif parsed.path == "/api/status":
                self._send_json(200, {
                    "status": "online",
                    "server": "Python Standard Library (http.server)",
                    "python_version": sys.version.split()[0],
                    "system": platform.system(),
                    "platform": platform.platform(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
            else:
                self.send_error(404, "Not Found")

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""
            try:
                data = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                data = {}

            if parsed.path == "/api/greet":
                name = data.get("name", "")
                self._send_json(200, {"message": greet(name)})
            elif parsed.path == "/api/add":
                try:
                    a = float(data.get("a", 0))
                    b = float(data.get("b", 0))
                    result = add(a, b)
                    formatted_result = int(result) if result.is_integer() else result
                    self._send_json(200, {
                        "result": formatted_result,
                        "expression": f"{a} + {b} = {formatted_result}",
                    })
                except Exception:
                    self._send_json(400, {"error": "Invalid numbers provided"})
            else:
                self.send_error(404, "Endpoint not found")

        def log_message(self, format, *args):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sys.stdout.write(f"[{timestamp}] {format % args}\n")

    def run_server(port: int = 5000):
        """Run the built-in HTTP server."""
        print(f"[*] Flask not detected. Starting Python http.server on http://0.0.0.0:{port}")
        server = HTTPServer(("0.0.0.0", port), StandaloneHandler)
        server.serve_forever()


if __name__ == "__main__":
    port_env = int(os.environ.get("PORT", 5000))
    run_server(port=port_env)
