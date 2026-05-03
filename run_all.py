"""Run everything — Bot + Personal Agent + Web Server."""

import os, sys, asyncio
from dotenv import load_dotenv
load_dotenv()

from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── Web Server (Render keep-alive + Admin Panel) ──────────────────────────
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from bot.web_admin import AdminWebHandler
        if AdminWebHandler.handle(self, self.path): return
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Asmo System Running")
    def log_message(self, *a): pass

def start_http():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

Thread(target=start_http, daemon=True).start()

# ── Bot ───────────────────────────────────────────────────────────────────
from bot.main import main as bot_main

# ── Personal Agent ────────────────────────────────────────────────────────
from personal_agent import run_agent

async def run_all():
    """Run bot and personal agent together."""
    api_id = os.environ.get("API_ID", "0")
    if api_id and api_id != "0":
        # Run both
        await asyncio.gather(
            bot_main(),
            run_agent(),
        )
    else:
        # Only bot
        await bot_main()

if __name__ == "__main__":
    asyncio.run(run_all())
