import os, sys
from dotenv import load_dotenv
load_dotenv()

# Render Web Service uchun port ochish
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def log_message(self, *args):
        pass

def start_http():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

Thread(target=start_http, daemon=True).start()

# Bot ishga tushirish
sys.path.insert(0, '/opt/render/project/src')
from bot.main import main
import asyncio
asyncio.run(main())
