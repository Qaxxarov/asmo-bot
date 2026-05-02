"""Order FSM — name → contact → details → saved → payment."""

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message,
)

from .. import database as db
from ..config import ADMIN_ID, logger
from ..keyboards import cancel_kb, main_menu_kb, order_review_kb, payment_kb
from ..locales import TEXTS, t

router = Router(name="order")


class OrderStates(StatesGroup):
    name    = State()
    contact = State()
    details = State()


def _lang(uid: int) -> str:
    return db.get_language(uid)


def _cancel_match():
    return F.text.in_({TEXTS[l]["btn_cancel"] for l in TEXTS})


def _menu_order_match():
    return F.text.in_({TEXTS[l]["menu_order"] for l in TEXTS})


# ── Cancel (works from any FSM state) ─────────────────────────────────────

@router.message(_cancel_match())
async def cancel_any(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id if message.from_user else 0
    lang = _lang(uid)
    await state.clear()
    await message.answer(t(lang, "cancel"), reply_markup=main_menu_kb(lang))


# ── Start order from service detail ───────────────────────────────────────

@router.callback_query(F.data.startswith("order:"))
async def cb_order_start(query: CallbackQuery, state: FSMContext) -> None:
    if not query.data or not query.from_user or not query.message:
        return
    try:
        sid = int(query.data.split(":", 1)[1])
    except ValueError:
        await query.answer()
        return

    svc = db.get_service(sid)
    lang = _lang(query.from_user.id)
    if not svc:
        await query.answer(t(lang, "order_no_service"), show_alert=True)
        return

    await state.update_data(service_id=sid, service_name=svc["name"], service_price=svc["price"])
    await state.set_state(OrderStates.name)
    await query.message.answer(t(lang, "order_intro"), reply_markup=cancel_kb(lang), parse_mode="HTML")
    await query.answer()


# ── Start order from "Buyurtma" menu button ───────────────────────────────

@router.message(_menu_order_match())
async def menu_order(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    lang = _lang(message.from_user.id)
    services = db.list_services()
    if not services:
        await message.answer(t(lang, "services_empty"))
        return
    # Show services list to pick from
    from ..keyboards import services_kb
    await message.answer(
        t(lang, "services_title"),
        reply_markup=services_kb(services, lang),
        parse_mode="HTML",
    )


# ── Step 1: Name ───────────────────────────────────────────────────────────

@router.message(OrderStates.name)
async def step_name(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    lang = _lang(message.from_user.id)
    name = (message.text or "").strip()
    if not name:
        return
    await state.update_data(name=name)
    await state.set_state(OrderStates.contact)
    await message.answer(t(lang, "order_ask_contact", name=name),
                         reply_markup=cancel_kb(lang), parse_mode="HTML")


# ── Step 2: Contact ────────────────────────────────────────────────────────

@router.message(OrderStates.contact)
async def step_contact(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    lang = _lang(message.from_user.id)
    contact = (message.text or "").strip()
    if not contact:
        return
    await state.update_data(contact=contact)
    await state.set_state(OrderStates.details)
    await message.answer(t(lang, "order_ask_details"),
                         reply_markup=cancel_kb(lang), parse_mode="HTML")


# ── Step 3: Details → save & notify ───────────────────────────────────────

@router.message(OrderStates.details)
async def step_details(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user:
        return
    lang = _lang(message.from_user.id)
    details = (message.text or "").strip()
    data = await state.get_data()

    order_id = db.create_order(
        user_id    = message.from_user.id,
        service_id = data.get("service_id"),
        name       = data.get("name", ""),
        contact    = data.get("contact", ""),
        details    = details,
    )
    db.add_request(
        message.from_user.id,
        "order",
        summary=f"{data.get('service_name','—')}: {details[:200]}",
        order_id=order_id,
    )

    # Keep order_id + price in state for payment flow
    await state.clear()
    await state.update_data(order_id=order_id, service_price=data.get("service_price","—"))

    # Confirm to user + show payment options
    await message.answer(
        t(lang, "order_saved", order_id=order_id),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await message.answer(
        t(lang, "payment_info", price=data.get("service_price", "—")),
        reply_markup=payment_kb(lang),
        parse_mode="HTML",
    )

    # Notify admin
    if ADMIN_ID:
        admin_text = t(
            "uz", "admin_new_order",
            order_id = order_id,
            name     = data.get("name", ""),
            contact  = data.get("contact", ""),
            service  = data.get("service_name", "—"),
            price    = data.get("service_price", "—"),
            details  = details[:300],
            user_id  = message.from_user.id,
        )
        # Append reply + open-chat buttons to order review kb
        base_rows = order_review_kb(order_id, "uz").inline_keyboard
        extra_row = [
            InlineKeyboardButton(text="✍️ Javob", callback_data=f"adm:reply:{message.from_user.id}"),
            InlineKeyboardButton(text="💬 Chat",  url=f"tg://user?id={message.from_user.id}"),
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=base_rows + [extra_row])
        try:
            await bot.send_message(ADMIN_ID, admin_text, reply_markup=kb, parse_mode="HTML")
            logger.info("Admin notified: new order=%s user=%s", order_id, message.from_user.id)
        except Exception as exc:
            logger.error("Failed to notify admin about order %s: %s", order_id, exc)


# ── Admin order approve/reject ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("ord:"))
async def cb_order_decision(query: CallbackQuery, bot: Bot) -> None:
    if not query.data or not query.from_user:
        return
    if query.from_user.id != ADMIN_ID:
        await query.answer()
        return

    parts = query.data.split(":")
    if len(parts) != 3:
        await query.answer()
        return
    _, action, oid_str = parts
    try:
        order_id = int(oid_str)
    except ValueError:
        await query.answer()
        return

    status  = "approved" if action == "approve" else "rejected"
    user_id = db.update_order_status(order_id, status)

    if user_id:
        user_lang = db.get_language(user_id)
        msg_key   = "user_order_approved" if status == "approved" else "user_order_rejected"
        try:
            await bot.send_message(user_id, t(user_lang, msg_key), parse_mode="HTML")
        except Exception as exc:
            logger.error("Failed to notify user %s about order status: %s", user_id, exc)

    if query.message:
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await query.answer("✅ OK")
