"""User-facing handlers: start, menu, services, AI chat, payment."""

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, PhotoSize, InlineKeyboardMarkup, InlineKeyboardButton

from .. import ai_handler, database as db
from ..config import ADMIN_ID, logger
from ..keyboards import (
    admin_payment_kb,
    admin_request_kb,
    language_kb,
    main_menu_kb,
    payment_kb,
    quick_order_kb,
    remove_kb,
    service_detail_kb,
    services_kb,
)
from ..locales import TEXTS, t

router = Router(name="user")


# ── Payment FSM ────────────────────────────────────────────────────────────

class PaymentStates(StatesGroup):
    waiting_receipt = State()


# ── Helpers ────────────────────────────────────────────────────────────────

def _lang(message: Message) -> str:
    return db.get_language(message.from_user.id) if message.from_user else "uz"


def _menu_match(key: str):
    return F.text.in_({TEXTS[l][key] for l in TEXTS})


# ── Start / Help ───────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(TEXTS["uz"]["choose_language"], reply_markup=language_kb())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    lang = _lang(message)
    await message.answer(
        t(lang, "welcome", name=message.from_user.full_name),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )


# ── Language selection ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("lang:"))
async def cb_set_language(query: CallbackQuery) -> None:
    if not query.data or not query.from_user or not query.message:
        return
    lang = query.data.split(":", 1)[1]
    if lang not in TEXTS:
        lang = "uz"
    db.set_language(query.from_user.id, lang)
    await query.message.edit_text(t(lang, "language_set"))
    await query.message.answer(
        t(lang, "welcome", name=query.from_user.full_name),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await query.answer()


# ── Main menu buttons ──────────────────────────────────────────────────────

@router.message(_menu_match("menu_change_lang"))
async def menu_change_lang(message: Message) -> None:
    await message.answer(TEXTS["uz"]["choose_language"], reply_markup=language_kb())


@router.message(_menu_match("menu_about"))
async def menu_about(message: Message) -> None:
    lang = _lang(message)
    await message.answer(t(lang, "about"), parse_mode="HTML")


@router.message(_menu_match("menu_portfolio"))
async def menu_portfolio(message: Message) -> None:
    lang = _lang(message)
    portfolio_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🌐 Portfolio saytni ochish",
            url="https://qaxxarov-portfolio.vercel.app"
        )],
        [InlineKeyboardButton(
            text="📸 Instagram",
            url="https://www.instagram.com/qaxxarov_98"
        ),
        InlineKeyboardButton(
            text="💬 Telegram",
            url="https://t.me/qaxxarov_98"
        )],
        [InlineKeyboardButton(
            text="🛒 Buyurtma berish",
            callback_data="ai:order"
        )],
    ])
    await message.answer(
        t(lang, "portfolio"),
        reply_markup=portfolio_kb,
        parse_mode="HTML",
    )


@router.message(_menu_match("menu_contact"))
async def menu_contact(message: Message) -> None:
    lang = _lang(message)
    await message.answer(t(lang, "contact"), parse_mode="HTML")


@router.message(_menu_match("menu_services"))
async def menu_services(message: Message) -> None:
    lang = _lang(message)
    services = db.list_services()
    if not services:
        await message.answer(t(lang, "services_empty"))
        return
    await message.answer(
        t(lang, "services_title"),
        reply_markup=services_kb(services, lang),
        parse_mode="HTML",
    )


# ── Service callbacks ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("svc:"))
async def cb_service(query: CallbackQuery) -> None:
    if not query.data or not query.from_user or not query.message:
        return
    lang = db.get_language(query.from_user.id)
    arg = query.data.split(":", 1)[1]

    if arg == "back":
        services = db.list_services()
        await query.message.edit_text(
            t(lang, "services_title"),
            reply_markup=services_kb(services, lang),
            parse_mode="HTML",
        )
        await query.answer()
        return

    try:
        sid = int(arg)
    except ValueError:
        await query.answer()
        return

    svc = db.get_service(sid)
    if not svc:
        await query.answer()
        return

    await query.message.edit_text(
        t(lang, "service_card",
          name=svc["name"], description=svc["description"], price=svc["price"]),
        reply_markup=service_detail_kb(sid, lang),
        parse_mode="HTML",
    )
    await query.answer()


# ── AI quick-action buttons ────────────────────────────────────────────────

@router.callback_query(F.data == "ai:order")
async def cb_ai_order(query: CallbackQuery) -> None:
    if not query.from_user or not query.message:
        return
    lang = db.get_language(query.from_user.id)
    services = db.list_services()
    if not services:
        await query.message.answer(t(lang, "services_empty"))
    else:
        await query.message.answer(
            t(lang, "services_title"),
            reply_markup=services_kb(services, lang),
            parse_mode="HTML",
        )
    await query.answer()


@router.callback_query(F.data == "ai:call_admin")
async def cb_ai_call_admin(query: CallbackQuery) -> None:
    if not query.from_user or not query.message:
        return
    user = query.from_user
    lang = db.get_language(user.id)

    last_msg = ai_handler.get_last_user_message(user.id) or "—"
    orders = db.get_user_orders(user.id)
    phone = orders[0]["contact"] if orders else "—"

    req_id = db.add_request(user.id, "admin_call", summary=last_msg[:300])

    if ADMIN_ID:
        try:
            await query.message.bot.send_message(
                ADMIN_ID,
                t("uz", "admin_new_call",
                  name=user.full_name or "—",
                  user_id=user.id,
                  username=user.username or "—",
                  phone=phone,
                  last_msg=last_msg[:300]),
                reply_markup=admin_request_kb(req_id, user.id, "uz"),
                parse_mode="HTML",
            )
            logger.info("Admin notified: call_admin req=%s user=%s", req_id, user.id)
        except Exception as exc:
            logger.error("Failed to notify admin (call_admin): %s", exc)

    await query.message.answer(t(lang, "admin_call_sent"))
    await query.answer()


# ── Payment flow ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "pay:receipt")
async def cb_pay_receipt(query: CallbackQuery, state: FSMContext) -> None:
    """User says they paid — ask for receipt photo."""
    if not query.from_user or not query.message:
        return
    lang = db.get_language(query.from_user.id)
    data = await state.get_data()
    order_id = data.get("order_id")
    price = data.get("service_price", "—")

    if not order_id:
        await query.answer()
        return

    payment_id = db.create_payment(order_id, query.from_user.id, price)
    await state.update_data(payment_id=payment_id)
    await state.set_state(PaymentStates.waiting_receipt)

    try:
        await query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await query.message.answer(t(lang, "payment_receipt_ask"), parse_mode="HTML")
    await query.answer()


@router.callback_query(F.data == "pay:later")
async def cb_pay_later(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or not query.message:
        return
    lang = db.get_language(query.from_user.id)
    await state.clear()
    try:
        await query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.answer(
        t(lang, "admin_call_sent"),
        reply_markup=main_menu_kb(lang),
    )
    await query.answer()


@router.message(PaymentStates.waiting_receipt, F.photo)
async def step_receipt_photo(message: Message, state: FSMContext) -> None:
    """Receive receipt photo, notify admin."""
    if not message.from_user or not message.photo:
        return
    lang = db.get_language(message.from_user.id)
    data = await state.get_data()
    payment_id = data.get("payment_id")
    order_id   = data.get("order_id")

    if not payment_id:
        await state.clear()
        await message.answer(t(lang, "unknown"), reply_markup=main_menu_kb(lang))
        return

    # Save best-quality photo file_id
    best: PhotoSize = max(message.photo, key=lambda p: p.file_size or 0)
    db.set_payment_receipt(payment_id, best.file_id)
    await state.clear()

    await message.answer(t(lang, "payment_receipt_received"), reply_markup=main_menu_kb(lang))

    # Notify admin with the receipt photo
    if ADMIN_ID:
        user = message.from_user
        price = data.get("service_price", "—")
        try:
            await message.bot.send_photo(
                ADMIN_ID,
                best.file_id,
                caption=t("uz", "admin_new_payment",
                          order_id=order_id or "—",
                          name=user.full_name or "—",
                          user_id=user.id,
                          amount=price),
                reply_markup=admin_payment_kb(payment_id, "uz"),
                parse_mode="HTML",
            )
            logger.info("Payment receipt forwarded to admin: pmt=%s order=%s", payment_id, order_id)
        except Exception as exc:
            logger.error("Failed to notify admin about payment: %s", exc)


@router.message(PaymentStates.waiting_receipt)
async def step_receipt_not_photo(message: Message) -> None:
    lang = _lang(message)
    await message.answer(t(lang, "payment_receipt_ask"), parse_mode="HTML")


# ── Admin payment decisions ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("pmt:"))
async def cb_payment_decision(query: CallbackQuery) -> None:
    if not query.from_user or not query.data:
        return
    if query.from_user.id != ADMIN_ID:
        await query.answer()
        return

    parts = query.data.split(":")
    if len(parts) != 3:
        await query.answer()
        return
    _, action, pid_str = parts
    try:
        pmt_id = int(pid_str)
    except ValueError:
        await query.answer()
        return

    status = "confirmed" if action == "confirm" else "rejected"
    user_id = db.update_payment_status(pmt_id, status)

    if user_id:
        user_lang = db.get_language(user_id)
        msg_key = "payment_confirmed" if status == "confirmed" else "payment_rejected"
        try:
            await query.message.bot.send_message(user_id, t(user_lang, msg_key), parse_mode="HTML")
        except Exception as exc:
            logger.error("Failed to notify user %s about payment: %s", user_id, exc)

    if query.message:
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await query.answer("✅ OK")


# ── AI chat fallback ───────────────────────────────────────────────────────

@router.message(F.text & ~F.text.startswith("/"))
async def ai_chat(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    # Don't hijack active FSM state
    if await state.get_state():
        return

    lang = db.get_language(message.from_user.id)
    try:
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass

    reply = await ai_handler.chat(message.from_user.id, lang, message.text)
    await message.answer(reply, reply_markup=quick_order_kb(lang), parse_mode="HTML")


@router.message()
async def fallback(message: Message) -> None:
    lang = _lang(message)
    await message.answer(t(lang, "unknown"), reply_markup=main_menu_kb(lang))
