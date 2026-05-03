import os, sys
from dotenv import load_dotenv
load_dotenv()

# Render Web Service uchun port ochish + Admin Web Panel
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Try admin panel first
        from bot.web_admin import AdminWebHandler
        if AdminWebHandler.handle_admin_request(self, self.path):
            return
        # Default — bot is running
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Asmo Creative AI Bot is running!")

    def log_message(self, *args):
        pass


def start_http():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


Thread(target=start_http, daemon=True).start()

# Bot ishga tushirish
from bot.main import main
import asyncio
asyncio.run(main())
