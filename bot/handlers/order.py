"""Order FSM — name → contact → details → saved. Payment only after admin sets price."""

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from .. import database as db
from ..config import ADMIN_ID, PAYMENT_CARD, PAYMENT_CARD_OWNER, logger
from ..keyboards import main_menu_kb, cancel_kb, payment_confirm_kb

router = Router(name="order")


class OrderStates(StatesGroup):
    name = State(); contact = State(); details = State()

class AdminPriceState(StatesGroup):
    price = State(); deadline = State()


# ── Cancel ─────────────────────────────────────────────────────────────────
@router.message(F.text == "❌ Bekor qilish")
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


# ── Start order ────────────────────────────────────────────────────────────
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


# ── Steps ──────────────────────────────────────────────────────────────────
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
    await message.answer("Zo'r! <b>Buyurtma tafsilotlarini</b> yozing:\n— Nima kerak?\n— Qanday uslubda?", reply_markup=cancel_kb(), parse_mode="HTML")

@router.message(OrderStates.details)
async def step_details(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user: return
    details = (message.text or "").strip()
    data = await state.get_data()
    order_id = db.create_order(message.from_user.id, data.get("service_id"), data.get("name",""), data.get("contact",""), details)
    await state.clear()

    await message.answer(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"📦 Raqam: <b>#{order_id}</b>\n\n"
        f"Admin buyurtmangizni ko'rib chiqadi va narx + muddatni belgilaydi.\n"
        f"📦 «Zakazlarim» tugmasidan kuzatib boring. 🙏",
        reply_markup=main_menu_kb(), parse_mode="HTML")

    if ADMIN_ID:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul + Narx", callback_data=f"ord:setprice:{order_id}"),
             InlineKeyboardButton(text="❌ Rad", callback_data=f"ord:reject:{order_id}")],
            [InlineKeyboardButton(text="💬 Chat", url=f"tg://user?id={message.from_user.id}")],
        ])
        try:
            await bot.send_message(ADMIN_ID,
                f"🆕 <b>Yangi buyurtma #{order_id}!</b>\n\n"
                f"👤 {data.get('name','—')}\n📞 {data.get('contact','—')}\n"
                f"🧠 <b>{data.get('service_name','—')}</b>\n📝 {details[:300]}\n"
                f"🆔 <code>{message.from_user.id}</code>",
                reply_markup=kb, parse_mode="HTML")
        except Exception as e: logger.error("Admin notify failed: %s", e)


# ── Admin: Set price + deadline ────────────────────────────────────────────
@router.callback_query(F.data.startswith("ord:setprice:"))
async def cb_setprice(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    oid = int(query.data.split(":")[2])
    await state.set_state(AdminPriceState.price)
    await state.update_data(admin_order_id=oid)
    await query.message.answer(f"💰 Buyurtma <b>#{oid}</b> uchun <b>narxni</b> yozing:\n<i>Misol: 200 000 so'm</i>", parse_mode="HTML")
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
    await message.answer("⏰ Endi <b>muddatni</b> yozing:\n<i>Misol: 3 kun, 1 hafta</i>", parse_mode="HTML")

@router.message(AdminPriceState.deadline)
async def admin_deadline(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or message.from_user.id != ADMIN_ID: return
    deadline = (message.text or "").strip()
    if not deadline: await message.answer("❗ Muddatni yozing:"); return
    data = await state.get_data()
    oid, price = data.get("admin_order_id"), data.get("admin_price", "—")
    await state.clear()
    if not oid: await message.answer("❗ Buyurtma topilmadi."); return

    db.update_order_price_deadline(oid, price, deadline)
    db.update_order_status(oid, "confirmed")
    await message.answer(f"✅ Buyurtma <b>#{oid}</b> tasdiqlandi!\n💰 {price}\n⏰ {deadline}", reply_markup=main_menu_kb(), parse_mode="HTML")

    order = db.get_order(oid)
    if order:
        try:
            await bot.send_message(order["user_id"],
                f"✅ <b>Buyurtmangiz tasdiqlandi!</b>\n\n"
                f"📦 Buyurtma: <b>#{oid}</b>\n💰 Narx: <b>{price}</b>\n⏰ Muddat: <b>{deadline}</b>\n\n"
                f"💳 <b>To'lov:</b>\n<code>{PAYMENT_CARD}</code>\n<b>{PAYMENT_CARD_OWNER}</b>\n\n"
                f"To'lovdan keyin chek rasmini yuboring 👇",
                reply_markup=payment_confirm_kb(oid), parse_mode="HTML")
        except Exception as e: logger.error("Client notify failed: %s", e)


# ── Admin: Reject / Start work / Done ──────────────────────────────────────
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

@router.callback_query(F.data.startswith("ord:startwork:"))
async def cb_startwork(query: CallbackQuery, bot: Bot) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    oid = int(query.data.split(":")[2])
    uid = db.update_order_status(oid, "in_progress")
    if uid:
        order = db.get_order(oid)
        dl = order.get("deadline", "—") if order else "—"
        try: await bot.send_message(uid, f"🔄 <b>Buyurtma #{oid} — ish boshlandi!</b>\n⏰ Muddat: <b>{dl}</b>\n\n📦 «Zakazlarim» dan kuzating.", parse_mode="HTML")
        except: pass
    try: await query.message.edit_reply_markup(reply_markup=None)
    except: pass
    await query.answer("🔄 Boshlandi")

@router.callback_query(F.data.startswith("ord:done:"))
async def cb_done(query: CallbackQuery, bot: Bot) -> None:
    if not query.from_user or query.from_user.id != ADMIN_ID: await query.answer(); return
    oid = int(query.data.split(":")[2])
    uid = db.update_order_status(oid, "done")
    if uid:
        try: await bot.send_message(uid, f"🎉 <b>Buyurtma #{oid} tayyor!</b>\nAdmin tez orada tayyor ishni yuboradi. 🚀", parse_mode="HTML")
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
    await query.message.answer(f"📸 Buyurtma <b>#{oid}</b> uchun to'lov chekini <b>rasm</b> sifatida yuboring:", parse_mode="HTML")
    await query.answer()
