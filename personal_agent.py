"""Shaxsiy Agent — @qaxxarov_98 akkauntidan ishlaydigan AI agent.
Kimdir sizga shaxsiy yozsa — agent siz o'rningizda javob beradi."""

import os, asyncio, logging
from telethon import TelegramClient, events

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agent")

API_ID   = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

AGENT_PROMPT = """Sen — Tursunmurod akaning shaxsiy yordamchisisan. Xuddi haqiqiy odam kabi gaplash.
Hech qachon "men AI man" yoki "men bot man" dema.

Tursunmurod aka — professional AI kontent yaratuvchi va dizayner (5+ yil).
Xizmatlar: AI avatar video, reklama video, intro/outro, foto, video tahrirlash, dizayn.
Portfolio: https://qaxxarov-portfolio.vercel.app

QOIDALAR:
1. Qisqa javob ber (1-3 jumla max). Tabiy gapir.
2. Narx aytma — "loyihaga qarab, gaplashamiz" de.
3. Doim suhbatni davom ettir.
4. Emoji oz ishlat — tabiy bo'lsin.
5. Mijozni ishontir va buyurtma botga yo'nalthir.
6. Tayyor bo'lsa: "Buyurtmani rasmiylashtirish uchun shu botdan o'ting 👉 https://t.me/AsmoCreativeAI_Bot" de
7. Chegirma/murakkab savol → "Tursunmurod aka bilan gaplashib beraman, biroz kuting 👌" de
8. Shaxsiy savollar (oila, yosh, ...) ga javob berma — mavzuni ishga qaytar."""

ROUTER_PROMPT = """Xabarni tahlil qil. Faqat 1 so'z javob ber:
- agent — oddiy salom, suhbat
- sales — xizmat, ish, narx so'rayapti
- redirect — tayyor, buyurtma bermoqchi
- escalate — chegirma, murakkab, maxsus sharth
- ignore — spam, reklama, bot, guruh xabari"""

import httpx

_histories: dict[int, list] = {}

async def _gemini(system: str, messages: list, max_tokens: int = 200) -> str:
    if not GEMINI_API_KEY: return ""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    contents = [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in messages]
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8},
    }
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(url, json=payload)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        logger.error("Gemini error: %s", e)
        return ""


async def detect_mode(text: str) -> str:
    r = await _gemini(ROUTER_PROMPT, [{"role": "user", "text": text}], 10)
    r = r.lower().strip()
    for m in ("redirect", "escalate", "sales", "ignore", "agent"):
        if m in r: return m
    return "agent"


async def respond(user_id: int, text: str) -> tuple[str, str]:
    mode = await detect_mode(text)

    if mode == "ignore":
        return "", "ignore"

    if mode == "redirect":
        return ("Zo'r 👌\nBuyurtmani rasmiylashtirish uchun shu botdan o'ting:\n"
                "👉 https://t.me/AsmoCreativeAI_Bot"), "redirect"

    if mode == "escalate":
        return "Bu masalani Tursunmurod aka bilan aniqlashtirib beraman 👌\nBiroz kuting!", "escalate"

    prompt = AGENT_PROMPT
    hist = _histories.setdefault(user_id, [])
    hist.append({"role": "user", "text": text})
    if len(hist) > 10: hist[:] = hist[-10:]

    reply = await _gemini(prompt, hist)
    if not reply:
        return "Hozir band, biroz keyin javob beraman 👌", "agent"
    hist.append({"role": "model", "text": reply})
    return reply, mode


async def run_agent():
    if not API_ID or not API_HASH:
        logger.warning("API_ID/API_HASH not set — personal agent disabled")
        return

    client = TelegramClient("asmo_agent_session", API_ID, API_HASH)
    await client.start(phone=os.environ.get("PHONE_NUMBER", "+998940774000"))
    me = await client.get_me()
    logger.info("Personal agent started: @%s (id=%s)", me.username, me.id)

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        # Faqat shaxsiy xabarlar
        if not event.is_private: return
        if event.sender_id == me.id: return  # O'ziga javob bermasin
        if event.sender_id == ADMIN_ID: return  # Adminning o'ziga javob bermasin

        text = event.raw_text
        if not text or len(text) < 1: return

        try:
            reply, mode = await respond(event.sender_id, text)

            if mode == "ignore" or not reply:
                return

            # 1-3 sek kutish — tabiy ko'rinsin
            await asyncio.sleep(1.5)
            await event.respond(reply)

            # Escalate — adminga xabar
            if mode == "escalate":
                try:
                    sender = await event.get_sender()
                    name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
                    username = sender.username or "—"
                    await client.send_message(ADMIN_ID,
                        f"⚠️ MUHIM MIJOZ!\n\n"
                        f"👤 {name} (@{username})\n"
                        f"💬 {text[:300]}\n"
                        f"🆔 {event.sender_id}\n\n"
                        f"Javob berish kerak!")
                except Exception as e:
                    logger.error("Escalate failed: %s", e)

            logger.info("Agent replied to %s [%s]: %s", event.sender_id, mode, reply[:50])

        except Exception as e:
            logger.error("Agent handler error: %s", e)

    logger.info("Personal agent is listening...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(run_agent())
