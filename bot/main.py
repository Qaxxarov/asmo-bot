"""Bot entry point — production-grade with auto-restart and keep-alive server."""

import asyncio
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .config import BOT_TOKEN, logger
from .database import init_db
from .handlers import get_root_router


# ── Tiny HTTP keep-alive server (prevents Replit sleep) ───────────────────

class _PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args):  # suppress default logging
        pass


def _start_keepalive(port: int = 8080) -> None:
    """Start a minimal HTTP server so Replit keeps the process alive."""
    try:
        server = HTTPServer(("0.0.0.0", port), _PingHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info("Keep-alive HTTP server started on port %s", port)
    except Exception as exc:
        logger.warning("Keep-alive server failed to start: %s", exc)


# ── Bot startup ────────────────────────────────────────────────────────────

async def main() -> None:
    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(get_root_router())

    me = await bot.get_me()
    logger.info("Bot started: @%s (id=%s)", me.username, me.id)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            handle_signals=True,
        )
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


# ── Entry point with auto-restart ─────────────────────────────────────────

def run() -> None:
    _start_keepalive()
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Stopped by user.")
            break
        except Exception as exc:
            logger.exception("Bot crashed: %s — restarting in 5s...", exc)
            time.sleep(5)


if __name__ == "__main__":
    run()
