"""Bot configuration — loaded from environment variables."""

import logging
import os
import sys

# ── Logging ────────────────────────────────────────────────────────────────
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("bot")

# ── Required ───────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set. Exiting.")
    sys.exit(1)

ADMIN_ID_RAW = os.environ.get("ADMIN_ID", "0").strip()
try:
    ADMIN_ID = int(ADMIN_ID_RAW)
except ValueError:
    ADMIN_ID = 0
if not ADMIN_ID:
    logger.warning("ADMIN_ID is not set — admin features disabled.")

# ── Gemini AI ──────────────────────────────────────────────────────────────
# Priority: Replit proxy > direct GEMINI_API_KEY
GEMINI_PROXY_BASE = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL", "").strip().rstrip("/")
GEMINI_PROXY_KEY  = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY", "").strip()
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL      = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip()
AI_HISTORY_LIMIT  = int(os.environ.get("AI_HISTORY_LIMIT", "8"))

# ── Database ───────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("DB_PATH", "bot.db")

# ── Contact & Payment ──────────────────────────────────────────────────────
TELEGRAM_USERNAME  = os.environ.get("TELEGRAM_USERNAME", "@qaxxarov_98")
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "@qaxxarov_98")
PHONE_NUMBER       = os.environ.get("PHONE_NUMBER", "+998940774000")
PAYMENT_CARD       = os.environ.get("PAYMENT_CARD", "8600 0000 0000 0000")
PAYMENT_CARD_OWNER = os.environ.get("PAYMENT_CARD_OWNER", "Qaxxarov")
