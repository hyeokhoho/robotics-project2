import http.server
import ssl
import os
import json
import base64
from datetime import datetime
from urllib.parse import urlparse

PORT = 8443
PHOTO_DIR = "photos"

os.makedirs(PHOTO_DIR, exist_ok=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/upload":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body.decode("utf-8"))
            image_data = data["image"]

            if "," in image_data:
                image_data = image_data.split(",", 1)[1]

            img_bytes = base64.b64decode(image_data)

            filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S_%f.jpg")
            filepath = os.path.join(PHOTO_DIR, filename)

            with open(filepath, "wb") as f:
                f.write(img_bytes)

            res = {
                "ok": True,
                "filename": filename,
                "url": f"/photos/{filename}"
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        except Exception as e:
            self.send_error(500, str(e))

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/list_photos":
            files = sorted(os.listdir(PHOTO_DIR), reverse=True)
            files = [f for f in files if f.lower().endswith(".jpg")]

            res = {
                "photos": [f"/photos/{f}" for f in files]
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        super().do_GET()


server_address = ("0.0.0.0", PORT)
httpd = http.server.HTTPServer(server_address, Handler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"Serving HTTPS on https://0.0.0.0:{PORT}")
print(f"Photo directory: {os.path.abspath(PHOTO_DIR)}")

httpd.serve_forever()
