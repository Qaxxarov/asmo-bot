"""User handlers — menu, services, portfolio, AI chat, payment receipt."""

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PhotoSize, InlineKeyboardMarkup, InlineKeyboardButton

from .. import database as db, ai_agent
from ..config import ADMIN_ID, PAYMENT_CARD, PAYMENT_CARD_OWNER, logger
from ..keyboards import main_menu_kb, services_kb, service_detail_kb, cancel_kb

router = Router(name="user")


# ── Start ──────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    if not message.from_user: return
    await state.clear()
    u = message.from_user
    source = "direct"
    if message.text and "start=" in message.text:
        parts = message.text.split(" ", 1)
        if len(parts) > 1: source = parts[1]
    db.upsert_user(u.id, u.username, u.full_name, source)

    await message.answer(
        f"👋 Salom, <b>{u.full_name}</b>!\n\n"
        f"🎬 <b>Qaxxarov Portfolio — AI Video & Foto Creator</b>ga xush kelibsiz!\n\n"
        f"Zamonaviy AI texnologiyalari bilan professional kontent yaratamiz:\n"
        f"  🤖 AI Avatar videolar\n"
        f"  📺 Reklama videolari\n"
        f"  🎬 Intro & Outro\n"
        f"  📸 Foto tayyorlash\n"
        f"  🎨 Dizayn & Motion Graphics\n\n"
        f"5+ yillik tajriba | 90+ mijoz | 98% mamnunlik\n\n"
        f"👇 Menyudan tanlang yoki erkin yozing — AI agent yordam beradi!",
        reply_markup=main_menu_kb(), parse_mode="HTML")


# ── Menu buttons ───────────────────────────────────────────────────────────
@router.message(F.text == "🛠 Xizmatlar")
async def menu_services(message: Message) -> None:
    svcs = db.list_services()
    if not svcs:
        await message.answer("⏳ Xizmatlar hali qo'shilmagan.")
        return
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
        "🖼 <b>Portfolio</b>\n\n"
        "🌐 https://qaxxarov-portfolio.vercel.app\n\n"
        "5+ yil | 90+ mijoz | 98% mamnunlik\n"
        "Brendingiz uchun ham shunday natijani xohlaysizmi? 👇",
        reply_markup=kb, parse_mode="HTML")


@router.message(F.text == "ℹ️ Biz haqimizda")
async def menu_about(message: Message) -> None:
    await message.answer(
        "🚀 <b>Tursunmurod Qaxxarov — AI Kontent Yaratuvchi</b>\n\n"
        "5+ yillik tajribaga ega grafik dizayner va AI kontent yaratuvchi.\n\n"
        "Texnologiyalar: Photoshop, CapCut, Midjourney, Veo, Kling, Runway\n\n"
        "📞 +998940774000\n💬 @qaxxarov_98\n📸 @qaxxarov_98",
        parse_mode="HTML")


@router.message(F.text == "📞 Aloqa")
async def menu_contact(message: Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Admin bilan gaplashish", url="https://t.me/qaxxarov_98")],
    ])
    await message.answer(
        "📞 <b>Bog'lanish</b>\n\n"
        "👤 @qaxxarov_98\n📱 +998940774000\n🕐 9:00 – 22:00 (Du – Sha)",
        reply_markup=kb, parse_mode="HTML")


# ── My Orders ──────────────────────────────────────────────────────────────
@router.message(F.text == "📦 Zakazlarim")
async def menu_my_orders(message: Message) -> None:
    if not message.from_user: return
    orders = db.get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📭 Sizda hali buyurtmalar yo'q.\n\nXizmatlardan birini tanlang 👇", reply_markup=main_menu_kb())
        return

    status_map = {
        "new": "🆕 Ko'rib chiqilmoqda", "confirmed": "✅ Tasdiqlangan",
        "paid": "💰 To'lov qabul qilindi", "in_progress": "🔄 Ish jarayonda",
        "done": "✅ Tayyor!", "rejected": "❌ Rad etilgan",
    }
    text = "📦 <b>Sizning buyurtmalaringiz:</b>\n\n"
    for o in orders[:10]:
        svc = db.get_service(o["service_id"]) if o.get("service_id") else None
        text += f"<b>#{o['id']}</b> — {svc['name'] if svc else '—'}\n"
        text += f"   Holat: {status_map.get(o['status'], o['status'])}\n"
        if o.get("agreed_price"): text += f"   💰 Narx: <b>{o['agreed_price']}</b>\n"
        if o.get("deadline"): text += f"   ⏰ Muddat: <b>{o['deadline']}</b>\n"
        text += f"   📅 {(o['created_at'] or '')[:16]}\n\n"
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


# ── Service callbacks ──────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("svc:"))
async def cb_service(query: CallbackQuery) -> None:
    if not query.data or not query.message: return
    arg = query.data.split(":", 1)[1]
    if arg == "back":
        svcs = db.list_services()
        await query.message.edit_text("🛠 <b>Xizmatlar</b>\n\nBirini tanlang:", reply_markup=services_kb(svcs), parse_mode="HTML")
        await query.answer(); return
    try: sid = int(arg)
    except ValueError: await query.answer(); return
    svc = db.get_service(sid)
    if not svc: await query.answer(); return
    await query.message.edit_text(
        f"<b>{svc['name']}</b>\n\n📋 {svc['description']}\n\n💰 Narxi: <b>{svc['price']}</b>",
        reply_markup=service_detail_kb(sid), parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data == "ai:order")
async def cb_ai_order(query: CallbackQuery) -> None:
    if not query.message: return
    svcs = db.list_services()
    await query.message.answer("🛠 <b>Xizmatlar</b>\n\nBirini tanlang:", reply_markup=services_kb(svcs), parse_mode="HTML")
    await query.answer()


# ── Payment receipt (photo) ────────────────────────────────────────────────
@router.message(F.photo)
async def receipt_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.photo: return
    current = await state.get_state()
    if current != "waiting_receipt": return

    data = await state.get_data()
    payment_id = data.get("payment_id")
    order_id = data.get("order_id")
    if not payment_id: return

    best: PhotoSize = max(message.photo, key=lambda p: p.file_size or 0)
    db.set_payment_receipt(payment_id, best.file_id)
    await state.clear()
    await message.answer("✅ Chek qabul qilindi!\n\nAdmin 15–30 daqiqa ichida tekshiradi. 🙏", reply_markup=main_menu_kb())

    if ADMIN_ID:
        try:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pmt:confirm:{payment_id}"),
                 InlineKeyboardButton(text="❌ Rad", callback_data=f"pmt:reject:{payment_id}")],
            ])
            await bot.send_photo(ADMIN_ID, best.file_id,
                caption=f"💳 <b>To'lov cheki!</b>\n📦 Buyurtma #{order_id}\n👤 {message.from_user.full_name}\n🆔 <code>{message.from_user.id}</code>",
                reply_markup=kb, parse_mode="HTML")
        except Exception as e:
            logger.error("Admin payment notify failed: %s", e)


# ── Payment decisions ──────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("pmt:"))
async def cb_payment(query: CallbackQuery, bot: Bot) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    parts = query.data.split(":")
    if len(parts) != 3: await query.answer(); return
    action, pid = parts[1], int(parts[2])
    status = "confirmed" if action == "confirm" else "rejected"
    user_id = db.update_payment_status(pid, status)
    if user_id:
        msg = "🎉 <b>To'lov tasdiqlandi!</b>\nBuyurtmangiz ishga tushdi! 🚀" if status == "confirmed" else "❌ <b>To'lov rad etildi.</b>\n@qaxxarov_98 ga murojaat qiling."
        try: await bot.send_message(user_id, msg, parse_mode="HTML")
        except: pass
    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.answer("✅ OK")


# ── AI Chat (fallback for free text) ───────────────────────────────────────
@router.message(F.text & ~F.text.startswith("/"))
async def ai_chat(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.text: return
    if await state.get_state(): return
    # Skip menu buttons
    menu_texts = {"🛠 Xizmatlar", "🛒 Buyurtma", "📦 Zakazlarim", "🖼 Portfolio", "ℹ️ Biz haqimizda", "📞 Aloqa", "❌ Bekor qilish"}
    if message.text in menu_texts: return

    try: await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    except: pass

    reply, mode = await ai_agent.chat(message.from_user.id, message.text)
    await message.answer(reply, parse_mode="HTML")

    # Escalate alert to admin
    if mode == "escalate" and ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID,
                f"⚠️ <b>MUHIM MIJOZ!</b>\n\n"
                f"👤 {message.from_user.full_name} (@{message.from_user.username or '—'})\n"
                f"💬 {message.text[:300]}\n"
                f"🆔 <code>{message.from_user.id}</code>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💬 Chat", url=f"tg://user?id={message.from_user.id}")],
                ]), parse_mode="HTML")
        except Exception as e:
            logger.error("Escalate notify failed: %s", e)
