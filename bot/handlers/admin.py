"""Admin panel — stats, clients, orders, services, broadcast, reply."""

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import database as db
from ..config import ADMIN_ID, logger
from ..keyboards import (
    admin_client_detail_kb,
    admin_clients_kb,
    admin_panel_kb,
    admin_services_kb,
    main_menu_kb,
)
from ..locales import t

router = Router(name="admin")


def _is_admin(uid: int) -> bool:
    return bool(ADMIN_ID) and uid == ADMIN_ID


# ── FSM groups ─────────────────────────────────────────────────────────────

class BroadcastState(StatesGroup):
    text = State()

class ServiceAddState(StatesGroup):
    name        = State()
    description = State()
    price       = State()

class ServiceDelState(StatesGroup):
    sid = State()

class AdminReplyState(StatesGroup):
    text = State()


# ── /admin command ─────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not message.from_user:
        return
    lang = db.get_language(message.from_user.id) or "uz"
    if not _is_admin(message.from_user.id):
        await message.answer(t(lang, "admin_only"))
        return
    await message.answer(
        t(lang, "admin_panel"),
        reply_markup=admin_panel_kb(lang),
        parse_mode="HTML",
    )


# ── admin:* callbacks ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:"))
async def cb_admin(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or not query.message or not query.data:
        return
    if not _is_admin(query.from_user.id):
        await query.answer()
        return

    lang   = db.get_language(query.from_user.id) or "uz"
    action = query.data.split(":", 1)[1]

    # ── Stats ──────────────────────────────────────────────────────────
    if action == "stats":
        s = db.stats()
        rs = db.revenue_stats()
        text = (
            "📊 <b>TO'LIQ STATISTIKA</b>\n\n"
            "👥 <b>Foydalanuvchilar</b>\n"
            f"   Bugun: <b>{rs['today_users']}</b> | Jami: <b>{rs['total_users']}</b>\n\n"
            "📦 <b>Buyurtmalar</b>\n"
            f"   Bugun: <b>{rs['today_orders']}</b>\n"
            f"   Bu oy: <b>{rs['month_orders']}</b>\n"
            f"   Jami: <b>{rs['total_orders']}</b>\n\n"
            "📋 <b>Holat bo'yicha</b>\n"
            f"   🆕 Yangi: <b>{rs['new_orders']}</b>\n"
            f"   🔄 Jarayonda: <b>{rs['active_orders']}</b>\n"
            f"   ✅ Tayyor: <b>{rs['done_orders']}</b>\n\n"
            "💰 <b>Daromad</b>\n"
            f"   Tasdiqlangan: <b>{rs['confirmed_count']}</b> ta\n"
            f"   Umumiy summa: <b>{rs['confirmed_sum']:,} so'm</b>\n"
            f"   ⏳ Kutilmoqda: <b>{rs['pending_payments']}</b>\n\n"
            "🏆 <b>Top xizmat</b>\n"
            f"   {rs['top_service']} ({rs['top_service_count']} ta buyurtma)"
        )
        # Recent orders
        if rs['recent_orders']:
            text += "\n\n📋 <b>Oxirgi 5 buyurtma:</b>"
            for o in rs['recent_orders']:
                status_map = {'new': '🆕', 'confirmed': '✅', 'in_progress': '🔄', 'done': '✅', 'rejected': '❌'}
                st = status_map.get(o.get('status',''), '❓')
                text += f"\n  {st} #{o['id']} — {o.get('svc_name','—')} — {o['name']}"
        await query.message.answer(text, parse_mode="HTML")

    # ── Orders ─────────────────────────────────────────────────────────
    elif action == "orders":
        orders = db.list_orders(20)
        if not orders:
            await query.message.answer(t(lang, "admin_orders_empty"))
        else:
            for o in orders:
                svc = db.get_service(o["service_id"]) if o["service_id"] else None
                await query.message.answer(
                    t(lang, "admin_order_card",
                      id      = o["id"],
                      name    = o["name"],
                      contact = o["contact"],
                      service = svc["name"] if svc else "—",
                      details = o["details"] or "—",
                      created = (o["created_at"] or "")[:16],
                      status  = t(lang, f"order_status_{o['status']}")),
                    parse_mode="HTML",
                )

    # ── Services ───────────────────────────────────────────────────────
    elif action == "services":
        services = db.list_services()
        if not services:
            await query.message.answer(
                t(lang, "admin_no_services"), reply_markup=admin_services_kb(lang)
            )
        else:
            lines = [t(lang, "admin_services_list")]
            for s in services:
                lines.append(f"<b>#{s['id']}</b> — {s['name']} ({s['price']})")
            await query.message.answer(
                "\n".join(lines),
                reply_markup=admin_services_kb(lang),
                parse_mode="HTML",
            )

    # ── Clients ────────────────────────────────────────────────────────
    elif action == "clients":
        clients = db.list_clients()
        if not clients:
            await query.message.answer(t(lang, "admin_clients_empty"))
        else:
            await query.message.answer(
                t(lang, "admin_clients_title"),
                reply_markup=admin_clients_kb(clients, lang),
                parse_mode="HTML",
            )

    # ── Payments ───────────────────────────────────────────────────────
    elif action == "payments":
        # Quick stats on payments
        s = db.stats()
        text = (
            f"💳 <b>To'lovlar</b>\n\n"
            f"✅ Tasdiqlangan: <b>{s['payments_ok']}</b>\n"
            f"⏳ Tekshirilayotgan: <b>{s['payments_pending']}</b>"
        )
        await query.message.answer(text, parse_mode="HTML")

    # ── Broadcast ──────────────────────────────────────────────────────
    elif action == "broadcast":
        await state.set_state(BroadcastState.text)
        await query.message.answer(t(lang, "admin_broadcast_ask"))

    # ── Service add/del ────────────────────────────────────────────────
    elif action == "svc_add":
        await state.set_state(ServiceAddState.name)
        await query.message.answer(t(lang, "admin_add_name"), parse_mode="HTML")
    elif action == "svc_del":
        await state.set_state(ServiceDelState.sid)
        await query.message.answer(t(lang, "admin_del_ask"), parse_mode="HTML")

    await query.answer()


# ── Broadcast flow ─────────────────────────────────────────────────────────

@router.message(BroadcastState.text)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        return
    lang = db.get_language(message.from_user.id) or "uz"
    text = message.text or message.caption or ""
    await state.clear()

    ok = fail = 0
    for uid in db.all_user_ids():
        try:
            await bot.send_message(uid, text, parse_mode="HTML")
            ok += 1
        except Exception as exc:
            fail += 1
            logger.warning("Broadcast failed uid=%s: %s", uid, exc)

    await message.answer(
        t(lang, "admin_broadcast_done", ok=ok, fail=fail),
        reply_markup=main_menu_kb(lang),
    )
    logger.info("Broadcast done: ok=%s fail=%s", ok, fail)


# ── Add service flow ───────────────────────────────────────────────────────

@router.message(ServiceAddState.name)
async def svc_add_name(message: Message, state: FSMContext) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        return
    lang = db.get_language(message.from_user.id) or "uz"
    await state.update_data(name=(message.text or "").strip())
    await state.set_state(ServiceAddState.description)
    await message.answer(t(lang, "admin_add_desc"), parse_mode="HTML")


@router.message(ServiceAddState.description)
async def svc_add_desc(message: Message, state: FSMContext) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        return
    lang = db.get_language(message.from_user.id) or "uz"
    await state.update_data(description=(message.text or "").strip())
    await state.set_state(ServiceAddState.price)
    await message.answer(t(lang, "admin_add_price"), parse_mode="HTML")


@router.message(ServiceAddState.price)
async def svc_add_price(message: Message, state: FSMContext) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        return
    lang = db.get_language(message.from_user.id) or "uz"
    data = await state.get_data()
    sid  = db.add_service(
        name        = data.get("name", ""),
        description = data.get("description", ""),
        price       = (message.text or "").strip(),
    )
    await state.clear()
    await message.answer(t(lang, "admin_add_done", sid=sid), reply_markup=main_menu_kb(lang))


# ── Delete service flow ────────────────────────────────────────────────────

@router.message(ServiceDelState.sid)
async def svc_del(message: Message, state: FSMContext) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        return
    lang = db.get_language(message.from_user.id) or "uz"
    await state.clear()
    try:
        sid = int((message.text or "").strip())
    except ValueError:
        await message.answer(t(lang, "admin_del_notfound"), reply_markup=main_menu_kb(lang))
        return
    ok  = db.delete_service(sid)
    key = "admin_del_done" if ok else "admin_del_notfound"
    await message.answer(t(lang, key), reply_markup=main_menu_kb(lang))


# ── Client detail view ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm:client:"))
async def cb_client_detail(query: CallbackQuery) -> None:
    if not query.from_user or not _is_admin(query.from_user.id):
        await query.answer()
        return
    lang = db.get_language(query.from_user.id) or "uz"
    try:
        uid = int(query.data.split(":")[2])
    except (ValueError, IndexError):
        await query.answer()
        return

    user = db.get_user(uid)
    if not user:
        await query.answer("Not found")
        return

    orders = db.get_user_orders(uid)
    reqs   = db.get_user_requests(uid)

    def _order_lines():
        if not orders:
            return t(lang, "admin_no_orders")
        lines = []
        for o in orders[:8]:
            svc    = db.get_service(o["service_id"]) if o["service_id"] else None
            status = t(lang, f"order_status_{o['status']}")
            lines.append(f"#{o['id']} • {svc['name'] if svc else '—'} • {status}")
        return "\n".join(lines)

    def _req_lines():
        if not reqs:
            return t(lang, "admin_no_reqs")
        lines = []
        for r in reqs[:8]:
            rtype  = t(lang, f"request_type_{r['type']}")
            status = t(lang, f"request_status_{r['status']}")
            lines.append(f"#{r['id']} • {rtype} • {status}")
        return "\n".join(lines)

    phone = orders[0]["contact"] if orders else "—"
    text  = t(lang, "admin_client_card",
              name      = user["full_name"] or "—",
              user_id   = user["user_id"],
              username  = user["username"] or "—",
              phone     = phone,
              created   = (user["created_at"] or "")[:16],
              orders_n  = len(orders),
              orders    = _order_lines(),
              reqs_n    = len(reqs),
              reqs      = _req_lines())

    await query.message.answer(
        text,
        reply_markup=admin_client_detail_kb(uid, lang),
        parse_mode="HTML",
    )
    await query.answer()


# ── Reply to user ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm:reply:"))
async def cb_reply_start(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or not _is_admin(query.from_user.id):
        await query.answer()
        return
    lang = db.get_language(query.from_user.id) or "uz"
    try:
        uid = int(query.data.split(":")[2])
    except (ValueError, IndexError):
        await query.answer()
        return
    await state.set_state(AdminReplyState.text)
    await state.update_data(target_user_id=uid)
    await query.message.answer(t(lang, "admin_reply_ask"))
    await query.answer()


@router.message(AdminReplyState.text)
async def do_reply(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        return
    lang = db.get_language(message.from_user.id) or "uz"
    data = await state.get_data()
    await state.clear()
    uid  = data.get("target_user_id")
    text = (message.text or "").strip()
    if not uid or not text:
        return
    user_lang = db.get_language(uid)
    try:
        await bot.send_message(uid, t(user_lang, "user_admin_reply", text=text), parse_mode="HTML")
        await message.answer(t(lang, "admin_reply_sent"))
        logger.info("Admin replied to user=%s", uid)
    except Exception as exc:
        await message.answer(t(lang, "admin_reply_failed", err=str(exc)))
        logger.error("Failed to reply to user=%s: %s", uid, exc)


# ── Resolve requests ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm:rreq:"))
async def cb_resolve_req(query: CallbackQuery) -> None:
    if not query.from_user or not _is_admin(query.from_user.id):
        await query.answer()
        return
    lang = db.get_language(query.from_user.id) or "uz"
    try:
        rid = int(query.data.split(":")[2])
    except (ValueError, IndexError):
        await query.answer()
        return
    db.set_request_status(rid, "resolved")
    if query.message:
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await query.answer(t(lang, "admin_resolved"))


@router.callback_query(F.data.startswith("adm:resolve_all:"))
async def cb_resolve_all(query: CallbackQuery) -> None:
    if not query.from_user or not _is_admin(query.from_user.id):
        await query.answer()
        return
    lang = db.get_language(query.from_user.id) or "uz"
    try:
        uid = int(query.data.split(":")[2])
    except (ValueError, IndexError):
        await query.answer()
        return
    n = db.resolve_user_open_requests(uid)
    await query.answer(f"✅ {n} ta hal qilindi")


@router.callback_query(F.data == "adm:clients_back")
async def cb_clients_back(query: CallbackQuery) -> None:
    if query.message:
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    await query.answer()
