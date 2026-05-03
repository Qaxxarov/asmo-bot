"""AI Agent — Gemini powered, dual mode: Agent + Sales closer."""

import asyncio
import httpx
from typing import Optional
from .config import GEMINI_API_KEY, logger

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash"]

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
- Tayyor bo'lsa → "Buyurtmani rasmiylashtirish uchun 🛒 Buyurtma tugmasini bosing" de
- Chegirma/maxsus sharth → Tursunmurod akaga uzatishingni ayt"""

SALES_PROMPT = """Sen — professional sotuv agent. Mijozni buyurtma berishga undash kerak.
1. Mijozning ehtiyojini tushun
2. Xizmatning qiymatini ko'rsat
3. Ishonch qozon (90+ mijoz, 98% mamnunlik, 5+ yil tajriba)
4. Harakatga unday → "🛒 Buyurtma tugmasini bosing"
Narx AYTMA. Qisqa gapir. Savol ber."""

ROUTER_PROMPT = """Mijoz xabarini tahlil qil. Faqat bitta so'z javob ber:
- "agent" — oddiy suhbat, salom, savol
- "sales" — xizmat so'ramoqda, qiziqmoqda, narx so'ramoqda
- "redirect" — tayyor, buyurtma bermoqchi, boshlaylik demoqda
- "escalate" — chegirma, maxsus sharth, murakkab talab
Faqat 1 so'z yoz."""

_histories: dict[int, list] = {}


async def _gemini(system: str, messages: list, max_tokens: int = 300) -> str:
    if not GEMINI_API_KEY:
        return ""

    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        contents = [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in messages]
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8},
        }
        try:
            async with httpx.AsyncClient(timeout=20) as c:
                r = await c.post(url, json=payload)
                if r.status_code == 429:
                    logger.warning("Gemini 429 on %s, trying next model...", model)
                    await asyncio.sleep(1)
                    continue
                r.raise_for_status()
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            logger.error("Gemini error (%s): %s", model, e)
            continue

    return ""


async def detect_mode(text: str) -> str:
    result = await _gemini(ROUTER_PROMPT, [{"role": "user", "text": text}], max_tokens=10)
    result = result.lower().strip()
    for mode in ("redirect", "escalate", "sales", "agent"):
        if mode in result: return mode
    return "agent"


async def chat(user_id: int, text: str) -> tuple[str, str]:
    mode = await detect_mode(text)

    if mode == "redirect":
        return "Zo'r 👌\n\n🛒 Buyurtma tugmasini bosib, xizmatni tanlang!", "redirect"

    if mode == "escalate":
        return "Bu masalani Tursunmurod aka bilan aniqlashtirib beraman 👌\nTez orada javob beraman!", "escalate"

    prompt = SALES_PROMPT if mode == "sales" else AGENT_PROMPT
    history = _histories.setdefault(user_id, [])
    history.append({"role": "user", "text": text})
    if len(history) > 12: history[:] = history[-12:]

    reply = await _gemini(prompt, history)
    if not reply:
        return "Hozir texnik nosozlik. Iltimos @qaxxarov_98 ga yozing.", mode

    history.append({"role": "model", "text": reply})
    return reply, mode
