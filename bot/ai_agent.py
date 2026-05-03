"""AI Agent — Gemini powered, dual mode: Agent + Sales closer."""

import httpx
from typing import Optional
from .config import GEMINI_API_KEY, GEMINI_MODEL, logger

AGENT_PROMPT = """Sen — Tursunmurod akaning shaxsiy agentisan. Hech qachon "men AI man" dema.
Sen xuddi haqiqiy odam kabi gaplash — qisqa, professional, do'stona.

Tursunmurod aka — professional AI kontent yaratuvchi va dizayner (5+ yil tajriba).
Xizmatlar: AI avatar video, reklama video, intro/outro, foto tayyorlash, video tahrirlash, dizayn & motion graphics.
Portfolio: https://qaxxarov-portfolio.vercel.app
Telegram: @qaxxarov_98 | Tel: +998940774000

QOIDALAR:
1. Qisqa javob ber (2-3 jumla). Uzun yozma.
2. Narx aytma — "loyihaga qarab belgilanadi, batafsil gaplashamiz" de.
3. Doim suhbatni davom ettir — savol ber.
4. Emoji ishlat lekin ortiqcha emas.
5. Mijozni ishontir va sotuvga yo'nalthir.
6. Chegirma so'rasa: "Bu masalani Tursunmurod aka bilan aniqlashtirib beraman 👌" de.

MIJOZ XABAR TURI VA JAVOB:
- Salom → Do'stona salom + nima yordam kerak deb so'ra
- Xizmat so'rasa → Ehtiyojni o'rgan, keyin buyurtma botga yo'nalthir
- Narx so'rasa → Aniq narx aytma, loyihaga qarab belgilanishini ayt
- Tayyor bo'lsa → "Buyurtmani rasmiylashtirish uchun shu botdan o'ting: 👉 https://t.me/AsmoCreativeAI_Bot" de
- Chegirma/maxsus sharth → Tursunmurod akaga uzatishingni ayt"""

SALES_PROMPT = """Sen — professional sotuv agent. Mijozni buyurtma berishga undash kerak.
Strategiya: AIDA (Attention → Interest → Desire → Action).

1. Mijozning ehtiyojini tushun
2. Xizmatning qiymatini ko'rsat (natija haqida gapir, vaqt/pul tejash)
3. Ishonch qozon (90+ mijoz, 98% mamnunlik, 5+ yil tajriba)
4. Harakatga unday → "Buyurtma uchun shu botdan o'ting: 👉 https://t.me/AsmoCreativeAI_Bot"

Narx AYTMA. Qisqa gapir. Savol ber."""

ROUTER_PROMPT = """Mijoz xabarini tahlil qil. Faqat bitta so'z javob ber:
- "agent" — oddiy suhbat, salom, savol
- "sales" — xizmat so'ramoqda, qiziqmoqda, narx so'ramoqda
- "redirect" — tayyor, buyurtma bermoqchi, boshlaylik demoqda
- "escalate" — chegirma, maxsus sharth, murakkab talab

Faqat 1 so'z yoz, boshqa hech narsa yozma."""

_histories: dict[int, list] = {}
_last_messages: dict[int, str] = {}


def _get_history(user_id: int) -> list:
    if user_id not in _histories:
        _histories[user_id] = []
    return _histories[user_id]


def get_last_user_message(user_id: int) -> Optional[str]:
    return _last_messages.get(user_id)


async def _gemini_call(system: str, messages: list, max_tokens: int = 300) -> str:
    if not GEMINI_API_KEY:
        return "AI vaqtincha ishlamayapti. Iltimos @qaxxarov_98 ga yozing."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    contents = []
    for m in messages:
        contents.append({"role": m["role"], "parts": [{"text": m["text"]}]})

    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8},
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        logger.error("Gemini error: %s", e)
        return "Hozir texnik nosozlik. Iltimos @qaxxarov_98 ga yozing."


async def detect_mode(text: str) -> str:
    """Detect: agent, sales, redirect, escalate."""
    result = await _gemini_call(ROUTER_PROMPT, [{"role": "user", "text": text}], max_tokens=10)
    result = result.lower().strip()
    for mode in ("redirect", "escalate", "sales", "agent"):
        if mode in result:
            return mode
    return "agent"


async def chat(user_id: int, text: str) -> tuple[str, str]:
    """Returns (response, mode)."""
    _last_messages[user_id] = text
    mode = await detect_mode(text)

    if mode == "redirect":
        return (
            "Zo'r 👌\n\n"
            "Buyurtmani tez va to'liq rasmiylashtirish uchun shu botdan o'ting:\n"
            "👉 https://t.me/AsmoCreativeAI_Bot",
            "redirect"
        )

    if mode == "escalate":
        return (
            "Bu masalani Tursunmurod aka bilan aniqlashtirib beraman 👌\n"
            "Tez orada javob beraman!",
            "escalate"
        )

    prompt = SALES_PROMPT if mode == "sales" else AGENT_PROMPT
    history = _get_history(user_id)
    history.append({"role": "user", "text": text})
    if len(history) > 12:
        history[:] = history[-12:]

    reply = await _gemini_call(prompt, history)
    history.append({"role": "model", "text": reply})

    return reply, mode
