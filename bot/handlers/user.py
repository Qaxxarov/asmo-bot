"""User handlers — menu, services, portfolio, AI chat."""

from datetime import datetime, timedelta
from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from .. import database as db, ai_agent
from ..config import ADMIN_ID, logger
from ..keyboards import main_menu_kb, services_kb, service_detail_kb

router = Router(name="user")


def _remaining(deadline_at: str) -> str:
    """Calculate remaining time from deadline_at ISO string."""
    if not deadline_at: return ""
    try:
        dl = datetime.fromisoformat(deadline_at)
        now = datetime.utcnow()
        diff = dl - now
        if diff.total_seconds() <= 0:
            return "⏰ Muddat tugagan"
        days = diff.days
        hours = diff.seconds // 3600
        mins = (diff.seconds % 3600) // 60
        if days > 0:
            return f"⏳ {days} kun {hours} soat qoldi"
        elif hours > 0:
            return f"⏳ {hours} soat {mins} daqiqa qoldi"
        else:
            return f"⏳ {mins} daqiqa qoldi"
    except:
        return ""


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    if not message.from_user: return
    await state.clear()
    u = message.from_user
    source = "direct"
    if message.text and " " in message.text:
        source = message.text.split(" ", 1)[1]
    db.upsert_user(u.id, u.username, u.full_name, source)
    await message.answer(
        f"👋 Salom, <b>{u.full_name}</b>!\n\n"
        f"🎬 <b>Qaxxarov Portfolio — AI Video & Foto Creator</b>ga xush kelibsiz!\n\n"
        f"Zamonaviy AI texnologiyalari bilan professional kontent yaratamiz:\n"
        f"  🤖 AI Avatar videolar\n  📺 Reklama videolari\n  🎬 Intro & Outro\n"
        f"  📸 Foto tayyorlash\n  🎨 Dizayn & Motion Graphics\n\n"
        f"5+ yillik tajriba | 90+ mijoz | 98% mamnunlik\n\n"
        f"👇 Menyudan tanlang yoki erkin yozing — AI agent yordam beradi!",
        reply_markup=main_menu_kb(), parse_mode="HTML")


@router.message(F.text == "🛠 Xizmatlar")
async def menu_services(message: Message) -> None:
    svcs = db.list_services()
    if not svcs: await message.answer("⏳ Xizmatlar hali qo'shilmagan."); return
    await message.answer("🛠 <b>Xizmatlar</b>\n\nBirini tanlang:", reply_markup=services_kb(svcs), parse_mode="HTML")


@router.message(F.text == "🖼 Portfolio")
async def menu_portfolio(message: Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Portfolio sayt", url="https://qaxxarov-portfolio.vercel.app")],
        [InlineKeyboardButton(text="📸 Instagram", url="https://www.instagram.com/qaxxarov_98"),
         InlineKeyboardButton(text="💬 Telegram", url="https://t.me/qaxxarov_98")],
        [InlineKeyboardButton(text="🛒 Buyurtma berish", callback_data="ai:order")],
    ])
    await message.answer(
        "🖼 <b>Portfolio</b>\n\n🌐 https://qaxxarov-portfolio.vercel.app\n\n"
        "5+ yil | 90+ mijoz | 98% mamnunlik\nBrendingiz uchun ham shunday natijani xohlaysizmi? 👇",
        reply_markup=kb, parse_mode="HTML")


@router.message(F.text == "ℹ️ Biz haqimizda")
async def menu_about(message: Message) -> None:
    await message.answer(
        "🚀 <b>Tursunmurod Qaxxarov — AI Kontent Yaratuvchi</b>\n\n"
        "5+ yillik tajribaga ega grafik dizayner va AI kontent yaratuvchi.\n\n"
        "Texnologiyalar: Photoshop, CapCut, Midjourney, Veo, Kling, Runway\n\n"
        "📞 +998940774000\n💬 @qaxxarov_98\n📸 @qaxxarov_98", parse_mode="HTML")


@router.message(F.text == "📞 Aloqa")
async def menu_contact(message: Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Admin bilan gaplashish", url="https://t.me/qaxxarov_98")]])
    await message.answer("📞 <b>Bog'lanish</b>\n\n👤 @qaxxarov_98\n📱 +998940774000\n🕐 9:00 – 22:00 (Du – Sha)", reply_markup=kb, parse_mode="HTML")


# ── Zakazlarim — real vaqt rejimida ────────────────────────────────────────
@router.message(F.text == "📦 Zakazlarim")
async def menu_my_orders(message: Message) -> None:
    if not message.from_user: return
    orders = db.get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📭 Sizda hali buyurtmalar yo'q.\n\nXizmatlardan birini tanlang 👇", reply_markup=main_menu_kb())
        return

    status_map = {
        "new": "🆕 Ko'rib chiqilmoqda",
        "confirmed": "✅ Tasdiqlangan — to'lov kutilmoqda",
        "paid": "💰 To'lov qabul qilindi",
        "in_progress": "🔄 Ish jarayonda",
        "done": "🎉 Tayyor!",
        "rejected": "❌ Rad etilgan",
    }

    text = "📦 <b>Sizning buyurtmalaringiz:</b>\n\n"
    for o in orders[:10]:
        svc = db.get_service(o["service_id"]) if o.get("service_id") else None
        status = status_map.get(o["status"], o["status"])

        text += f"━━━━━━━━━━━━━━━\n"
        text += f"<b>#{o['id']}</b> — {svc['name'] if svc else '—'}\n"
        text += f"📋 Holat: {status}\n"

        if o.get("agreed_price"):
            text += f"💰 Narx: <b>{o['agreed_price']}</b>\n"
        if o.get("deadline"):
            text += f"📅 Muddat: <b>{o['deadline']}</b>\n"

        # Real-time countdown
        if o["status"] == "in_progress" and o.get("deadline_at"):
            remaining = _remaining(o["deadline_at"])
            if remaining:
                text += f"{remaining}\n"
        elif o["status"] == "in_progress" and o.get("deadline"):
            text += f"⏳ Tayyor bo'lish: <b>{o['deadline']}</b>\n"

        if o["status"] == "done":
            text += "🎉 Buyurtmangiz tayyor! Admin tez orada yuboradi.\n"

        text += f"📅 Buyurtma sanasi: {(o['created_at'] or '')[:16]}\n\n"

    text += "━━━━━━━━━━━━━━━\n💡 <i>Yangilash uchun yana «📦 Zakazlarim» bosing</i>"
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


# ── Service detail ─────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("svc:"))
async def cb_service(query: CallbackQuery) -> None:
    if not query.data or not query.message: return
    arg = query.data.split(":", 1)[1]
    if arg == "back":
        svcs = db.list_services()
        await query.message.edit_text("🛠 <b>Xizmatlar</b>\n\nBirini tanlang:", reply_markup=services_kb(svcs), parse_mode="HTML")
        await query.answer(); return
    try: sid = int(arg)
    except: await query.answer(); return
    svc = db.get_service(sid)
    if not svc: await query.answer(); return
    await query.message.edit_text(
        f"<b>{svc['name']}</b>\n\n"
        f"{svc['description']}\n\n"
        f"{'━'*20}\n"
        f"{svc['price']}\n\n"
        f"📌 To'liq narx va shartlar — admin bilan kelishiladi\n"
        f"👇 Buyurtma bering yoki admin bilan bog'laning:",
        reply_markup=service_detail_kb(sid), parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data == "ai:order")
async def cb_ai_order(query: CallbackQuery) -> None:
    if not query.message: return
    svcs = db.list_services()
    await query.message.answer("🛠 <b>Xizmatlar</b>\n\nBirini tanlang:", reply_markup=services_kb(svcs), parse_mode="HTML")
    await query.answer()


# ── AI Chat ────────────────────────────────────────────────────────────────
@router.message(F.text & ~F.text.startswith("/"))
async def ai_chat(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.text: return
    if await state.get_state(): return
    menu_texts = {"🛠 Xizmatlar", "🛒 Buyurtma", "📦 Zakazlarim", "🖼 Portfolio", "ℹ️ Biz haqimizda", "📞 Aloqa", "❌ Bekor qilish"}
    if message.text in menu_texts: return

    try: await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    except: pass

    reply, mode = await ai_agent.chat(message.from_user.id, message.text)
    await message.answer(reply, parse_mode="HTML")

    if mode == "escalate" and ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID,
                f"⚠️ <b>MUHIM MIJOZ!</b>\n\n👤 {message.from_user.full_name} (@{message.from_user.username or '—'})\n💬 {message.text[:300]}\n🆔 <code>{message.from_user.id}</code>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💬 Chat", url=f"tg://user?id={message.from_user.id}")]]),
                parse_mode="HTML")
        except Exception as e: logger.error("Escalate failed: %s", e)
