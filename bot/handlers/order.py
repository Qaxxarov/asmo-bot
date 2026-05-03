"""Order FSM + Admin price/deadline + Payment + Receipt."""

import re
from datetime import datetime, timedelta
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, PhotoSize

from .. import database as db
from ..config import ADMIN_ID, PAYMENT_CARD, PAYMENT_CARD_OWNER, logger
from ..keyboards import main_menu_kb, cancel_kb, payment_confirm_kb

router = Router(name="order")

class OrderStates(StatesGroup):
    name = State(); contact = State(); details = State()

class AdminPriceState(StatesGroup):
    price = State(); deadline = State()


def _parse_deadline_to_datetime(deadline_text: str) -> str:
    """Parse '3 kun', '1 soat', '5 soat', '1 hafta' etc to ISO datetime."""
    text = deadline_text.lower().strip()
    now = datetime.utcnow()
    try:
        # Try direct date first
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%d.%m.%Y"):
            try: return datetime.strptime(text, fmt).isoformat(sep=" ", timespec="seconds")
            except: pass

        # Parse relative
        nums = re.findall(r'(\d+)', text)
        if not nums: return ""
        n = int(nums[0])
        if "soat" in text or "hour" in text:
            dt = now + timedelta(hours=n)
        elif "daqiqa" in text or "minut" in text or "min" in text:
            dt = now + timedelta(minutes=n)
        elif "hafta" in text or "week" in text:
            dt = now + timedelta(weeks=n)
        elif "kun" in text or "day" in text:
            dt = now + timedelta(days=n)
        elif "oy" in text or "month" in text:
            dt = now + timedelta(days=n*30)
        else:
            dt = now + timedelta(days=n)  # Default to days
        return dt.isoformat(sep=" ", timespec="seconds")
    except:
        return ""


# ── Cancel ─────────────────────────────────────────────────────────────────
@router.message(F.text == "❌ Bekor qilish")
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


# ── Start order from service ───────────────────────────────────────────────
@router.callback_query(F.data.startswith("order:"))
async def cb_order(query: CallbackQuery, state: FSMContext) -> None:
    if not query.data or not query.from_user: return
    try: sid = int(query.data.split(":")[1])
    except: await query.answer(); return
    svc = db.get_service(sid)
    if not svc: await query.answer("Xizmat topilmadi", show_alert=True); return
    await state.update_data(service_id=sid, service_name=svc["name"])
    await state.set_state(OrderStates.name)
    await query.message.answer("📝 <b>Buyurtma berish</b>\n\nAvval <b>ismingizni</b> yozing:", reply_markup=cancel_kb(), parse_mode="HTML")
    await query.answer()


@router.message(F.text == "🛒 Buyurtma")
async def menu_order(message: Message) -> None:
    svcs = db.list_services()
    if not svcs: await message.answer("Xizmatlar yo'q."); return
    from ..keyboards import services_kb
    await message.answer("🛠 Xizmat tanlang:", reply_markup=services_kb(svcs), parse_mode="HTML")


# ── Order Steps ────────────────────────────────────────────────────────────
@router.message(OrderStates.name)
async def step_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name or len(name) < 2: await message.answer("⚠️ Ismingizni yozing:"); return
    await state.update_data(name=name)
    await state.set_state(OrderStates.contact)
    await message.answer(f"Rahmat, <b>{name}</b> ✅\n\n<b>Telefon</b> yoki <b>username</b>ingizni yuboring:", reply_markup=cancel_kb(), parse_mode="HTML")

@router.message(OrderStates.contact)
async def step_contact(message: Message, state: FSMContext) -> None:
    contact = (message.text or "").strip()
    if not contact: await message.answer("⚠️ Kontakt yozing:"); return
    await state.update_data(contact=contact)
    await state.set_state(OrderStates.details)
    await message.answer("Zo'r! <b>Buyurtma tafsilotlarini</b> yozing:\n— Nima kerak?\n— Qanday uslubda?\n— Qo'shimcha izoh", reply_markup=cancel_kb(), parse_mode="HTML")

@router.message(OrderStates.details)
async def step_details(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user: return
    details = (message.text or "").strip()
    data = await state.get_data()
    oid = db.create_order(message.from_user.id, data.get("service_id"), data.get("name",""), data.get("contact",""), details)
    await state.clear()

    await message.answer(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"📦 Raqam: <b>#{oid}</b>\n\n"
        f"Admin buyurtmangizni ko'rib chiqadi, narx va muddatni belgilaydi.\n"
        f"Sizga xabar yuboriladi.\n\n"
        f"📦 «Zakazlarim» tugmasidan kuzatib boring 🙏",
        reply_markup=main_menu_kb(), parse_mode="HTML")

    if ADMIN_ID:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul + Narx", callback_data=f"ord:setprice:{oid}"),
             InlineKeyboardButton(text="❌ Rad", callback_data=f"ord:reject:{oid}")],
            [InlineKeyboardButton(text="💬 Chat", url=f"tg://user?id={message.from_user.id}")],
        ])
        try:
            await bot.send_message(ADMIN_ID,
                f"🆕 <b>Yangi buyurtma #{oid}!</b>\n\n"
                f"👤 {data.get('name','—')}\n📞 {data.get('contact','—')}\n"
                f"🧠 <b>{data.get('service_name','—')}</b>\n📝 {details[:300]}\n"
                f"🆔 <code>{message.from_user.id}</code>",
                reply_markup=kb, parse_mode="HTML")
        except Exception as e: logger.error("Admin notify: %s", e)


# ── Admin: Set price ───────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("ord:setprice:"))
async def cb_setprice(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    oid = int(query.data.split(":")[2])
    await state.set_state(AdminPriceState.price)
    await state.update_data(admin_order_id=oid)
    await query.message.answer(f"💰 Buyurtma <b>#{oid}</b> uchun <b>narxni</b> yozing:\n<i>Misol: 300 000 so'm</i>", parse_mode="HTML")
    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.answer()

@router.message(AdminPriceState.price)
async def admin_price(message: Message, state: FSMContext) -> None:
    if not message.from_user or message.from_user.id != ADMIN_ID: return
    price = (message.text or "").strip()
    if not price: await message.answer("❗ Narxni yozing:"); return
    await state.update_data(admin_price=price)
    await state.set_state(AdminPriceState.deadline)
    await message.answer("⏰ Endi <b>muddatni</b> yozing:\n<i>Misol: 3 kun, 1 soat, 1 hafta, 2025-06-01</i>", parse_mode="HTML")


# ── Admin: Set deadline ────────────────────────────────────────────────────
@router.message(AdminPriceState.deadline)
async def admin_deadline(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or message.from_user.id != ADMIN_ID: return
    deadline = (message.text or "").strip()
    if not deadline: await message.answer("❗ Muddatni yozing:"); return

    data = await state.get_data()
    oid, price = data.get("admin_order_id"), data.get("admin_price", "—")
    await state.clear()
    if not oid: await message.answer("❗ Buyurtma topilmadi."); return

    # Calculate deadline datetime
    deadline_at = _parse_deadline_to_datetime(deadline)

    db.update_order_price_deadline(oid, price, deadline, deadline_at)
    db.update_order_status(oid, "confirmed")

    await message.answer(
        f"✅ Buyurtma <b>#{oid}</b> tasdiqlandi!\n"
        f"💰 {price}\n⏰ {deadline}\n"
        f"Mijozga to'lov xabari yuborildi.",
        reply_markup=main_menu_kb(), parse_mode="HTML")

    order = db.get_order(oid)
    if order:
        try:
            await bot.send_message(order["user_id"],
                f"✅ <b>Buyurtmangiz tasdiqlandi!</b>\n\n"
                f"📦 Buyurtma: <b>#{oid}</b>\n"
                f"💰 Narx: <b>{price}</b>\n"
                f"⏰ Tayyor bo'lish muddati: <b>{deadline}</b>\n\n"
                f"💳 <b>To'lov ma'lumotlari:</b>\n"
                f"<code>{PAYMENT_CARD}</code>\n"
                f"<b>{PAYMENT_CARD_OWNER}</b>\n\n"
                f"To'lovni amalga oshirgandan keyin chek rasmini yuboring 👇",
                reply_markup=payment_confirm_kb(oid), parse_mode="HTML")
        except Exception as e: logger.error("Client notify: %s", e)


# ── Admin: Reject ──────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("ord:reject:"))
async def cb_reject(query: CallbackQuery, bot: Bot) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    oid = int(query.data.split(":")[2])
    uid = db.update_order_status(oid, "rejected")
    if uid:
        try: await bot.send_message(uid, f"❌ Buyurtma #{oid} rad etildi.\n@qaxxarov_98 ga murojaat qiling.", parse_mode="HTML")
        except: pass
    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.answer("❌ Rad etildi")


# ── Admin: Start work ─────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("ord:startwork:"))
async def cb_startwork(query: CallbackQuery, bot: Bot) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    oid = int(query.data.split(":")[2])
    db.set_work_started(oid)
    order = db.get_order(oid)
    uid = order["user_id"] if order else None
    dl = order.get("deadline", "—") if order else "—"
    if uid:
        try:
            await bot.send_message(uid,
                f"🔄 <b>Buyurtma #{oid} — tayyorlash boshlandi!</b>\n\n"
                f"🧠 Sizning xizmatingizni tayyorlashni boshladik!\n"
                f"⏰ Tayyor bo'lish muddati: <b>{dl}</b>\n\n"
                f"📦 «Zakazlarim» bo'limida tayyor bo'lish vaqtini\n"
                f"real vaqt rejimida kuzatib borishingiz mumkin 👀",
                parse_mode="HTML")
        except: pass
    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.answer("🔄 Ish boshlandi")


# ── Admin: Done ────────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("ord:done:"))
async def cb_done(query: CallbackQuery, bot: Bot) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    oid = int(query.data.split(":")[2])
    uid = db.update_order_status(oid, "done")
    if uid:
        try: await bot.send_message(uid,
            f"🎉 <b>Buyurtma #{oid} tayyor!</b>\n\n"
            f"Admin tez orada tayyor ishni yuboradi! 🚀\n"
            f"Savollar bo'lsa: @qaxxarov_98",
            parse_mode="HTML")
        except: pass
    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.answer("✅ Tayyor!")


# ── Client: Start payment ─────────────────────────────────────────────────
@router.callback_query(F.data.startswith("pay:start:"))
async def cb_pay_start(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user: return
    oid = int(query.data.split(":")[2])
    order = db.get_order(oid)
    if not order: await query.answer("Topilmadi"); return
    pid = db.create_payment(oid, query.from_user.id, order.get("agreed_price") or "—")
    await state.update_data(payment_id=pid, order_id=oid)
    await state.set_state("waiting_receipt")
    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.message.answer(
        f"📸 Buyurtma <b>#{oid}</b> uchun to'lov chekini <b>rasm</b> sifatida yuboring:\n\n"
        f"💳 Karta: <code>{PAYMENT_CARD}</code>\n<b>{PAYMENT_CARD_OWNER}</b>",
        parse_mode="HTML")
    await query.answer()


# ── Receipt photo ──────────────────────────────────────────────────────────
@router.message(F.photo)
async def receipt_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.photo: return
    current = await state.get_state()
    if current != "waiting_receipt": return

    data = await state.get_data()
    pid, oid = data.get("payment_id"), data.get("order_id")
    if not pid: await state.clear(); return

    best: PhotoSize = max(message.photo, key=lambda p: p.file_size or 0)
    db.set_payment_receipt(pid, best.file_id)
    await state.clear()
    await message.answer("✅ <b>Chek qabul qilindi!</b>\n\nAdmin 15–30 daqiqa ichida tekshiradi.\nBuyurtmangiz holatini «📦 Zakazlarim» dan kuzating 🙏", reply_markup=main_menu_kb(), parse_mode="HTML")

    if ADMIN_ID:
        try:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pmt:confirm:{pid}"),
                 InlineKeyboardButton(text="❌ Rad", callback_data=f"pmt:reject:{pid}")]])
            await bot.send_photo(ADMIN_ID, best.file_id,
                caption=f"💳 <b>To'lov cheki!</b>\n📦 Buyurtma #{oid}\n👤 {message.from_user.full_name}\n🆔 <code>{message.from_user.id}</code>",
                reply_markup=kb, parse_mode="HTML")
        except Exception as e: logger.error("Admin payment notify: %s", e)


# ── Payment confirm/reject ────────────────────────────────────────────────
@router.callback_query(F.data.startswith("pmt:"))
async def cb_payment(query: CallbackQuery, bot: Bot) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    parts = query.data.split(":")
    if len(parts) != 3: await query.answer(); return
    action, pid = parts[1], int(parts[2])
    status = "confirmed" if action == "confirm" else "rejected"
    uid = db.update_payment_status(pid, status)

    if status == "confirmed":
        payment = db.get_payment(pid)
        if payment:
            db.update_order_status(payment["order_id"], "paid")
            # Notify client: payment confirmed, work starting
            if uid:
                try:
                    await bot.send_message(uid,
                        f"🎉 <b>To'lov tasdiqlandi!</b>\n\n"
                        f"Buyurtmangiz ishga tushdi! 🚀\n"
                        f"📦 «Zakazlarim» bo'limida tayyor bo'lish vaqtini kuzating.",
                        parse_mode="HTML")
                except: pass
    elif uid:
        try: await bot.send_message(uid, "❌ <b>To'lov rad etildi.</b>\n@qaxxarov_98 ga murojaat qiling.", parse_mode="HTML")
        except: pass

    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.answer("✅ OK")
