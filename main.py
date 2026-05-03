import os, sys, asyncio
from dotenv import load_dotenv
load_dotenv()

from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from bot.web_admin import AdminWebHandler
        if AdminWebHandler.handle(self, self.path): return
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Asmo Creative AI Bot is running!")
    def log_message(self, *a): pass

def start_http():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

Thread(target=start_http, daemon=True).start()

from bot.main import main
asyncio.run(main())
