"""Configuration — loaded from environment."""

import logging, os, sys

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", stream=sys.stdout)
logger = logging.getLogger("bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN not set"); sys.exit(1)

ADMIN_ID_RAW = os.environ.get("ADMIN_ID", "0").strip()
try: ADMIN_ID = int(ADMIN_ID_RAW)
except ValueError: ADMIN_ID = 0

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip()

API_ID   = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "").strip()
PHONE    = os.environ.get("PHONE_NUMBER", "+998940774000").strip()

DB_PATH = os.environ.get("DB_PATH", "bot.db")

TELEGRAM_USERNAME  = os.environ.get("TELEGRAM_USERNAME", "@qaxxarov_98")
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "@qaxxarov_98")
PHONE_NUMBER       = os.environ.get("PHONE_NUMBER", "+998940774000")
PAYMENT_CARD       = os.environ.get("PAYMENT_CARD", "9860 0866 0228 9208")
PAYMENT_CARD_OWNER = os.environ.get("PAYMENT_CARD_OWNER", "Qaxxarov T")
