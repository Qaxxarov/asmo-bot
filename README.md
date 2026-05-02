# AI Studio Bot — Production Ready

## 📁 Fayl tuzilmasi

```
bot/
├── __init__.py
├── main.py          ← Ishga tushirish nuqtasi (keep-alive + auto-restart)
├── config.py        ← .env dan o'qish
├── database.py      ← SQLite (WAL mode, to'liq tranzaktsiyalar)
├── locales.py       ← O'zbek / Rus tillari
├── keyboards.py     ← Barcha klaviaturalar (2-per-row dizayn)
├── ai_handler.py    ← Gemini AI (ishonchli, to'liq xato boshqaruv)
└── handlers/
    ├── __init__.py
    ├── user.py      ← Asosiy menyular, AI chat, to'lov flow
    ├── order.py     ← Buyurtma FSM
    └── admin.py     ← Admin panel
```

## ⚙️ O'rnatish

### 1. Environment o'zgaruvchilarini sozlang (Replit Secrets):

| Kalit              | Tavsif                     |
|--------------------|---------------------------|
| `BOT_TOKEN`        | BotFather dan token        |
| `ADMIN_ID`         | Sizning Telegram ID'ingiz  |
| `GEMINI_API_KEY`   | Google AI Studio API key   |
| `PAYMENT_CARD`     | Karta raqami               |
| `PAYMENT_CARD_OWNER` | Karta egasi             |
| `TELEGRAM_USERNAME`| Telegram username          |
| `INSTAGRAM_USERNAME`| Instagram username        |
| `PHONE_NUMBER`     | Telefon raqam              |

### 2. Ishga tushirish:

```bash
pip install -r requirements.txt
python -m bot.main
```

## 🚀 Replit'da 24/7 ishlash

Bot `main.py` ichida **keep-alive HTTP server** (port 8080) o'rnatilgan.
Bu Replit'ning uyqu rejimiga tushishini oldini oladi.

Qo'shimcha ishonchlilik uchun [UptimeRobot](https://uptimerobot.com) da
botingiz URL'ini (Replit webview URL) har 5 daqiqada ping qiling.

## ✅ Qo'shilgan yangi imkoniyatlar

1. **To'lov tizimi** — karta raqamga o'tkazma + chek rasm yuborish + admin tasdiqlashi
2. **Keep-alive server** — Replit'da 24/7 ishlash
3. **Auto-restart** — bot crash bo'lsa, 5 soniyada qayta ishga tushadi
4. **AI tuzatildi** — proper Gemini API turns, timeout, 429/401 xato boshqaruv
5. **Faqat to'g'ri sotuv** — AI faqat rasm, video, bot sotadi (sayt emas)
6. **Admin to'lov tasdiqlash** — chek foto adminga ketadi, 1 tugma tasdiqlash
7. **2-per-row UI** — yangi toza dizayn
8. **Instagram & Telegram** — aloqa bo'limida ikkalasi ham
