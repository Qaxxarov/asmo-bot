"""Admin panel — /admin command, stats, broadcast."""

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import database as db
from ..config import ADMIN_ID, logger
from ..keyboards import admin_panel_kb, admin_order_kb, main_menu_kb

router = Router(name="admin")

def _is_admin(uid: int) -> bool:
    return bool(ADMIN_ID) and uid == ADMIN_ID

class BroadcastState(StatesGroup):
    text = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer("⛔ Faqat admin uchun."); return
    await message.answer("🛠 <b>Admin panel</b>\n\nAmalni tanlang:", reply_markup=admin_panel_kb(), parse_mode="HTML")


@router.callback_query(F.data.startswith("admin:"))
async def cb_admin(query: CallbackQuery, state: FSMContext) -> None:
    if not query.from_user or not _is_admin(query.from_user.id): await query.answer(); return
    action = query.data.split(":", 1)[1]

    if action == "stats":
        s = db.stats()
        text = (
            "📊 <b>STATISTIKA</b>\n\n"
            f"👥 Foydalanuvchilar: bugun <b>{s['today_users']}</b> | jami <b>{s['total_users']}</b>\n\n"
            f"📦 Buyurtmalar:\n"
            f"   Bugun: <b>{s['today_orders']}</b>\n"
            f"   Bu oy: <b>{s['month_orders']}</b>\n"
            f"   Jami: <b>{s['total_orders']}</b>\n\n"
            f"📋 Holat:\n"
            f"   🆕 Yangi: <b>{s['new_orders']}</b>\n"
            f"   🔄 Jarayonda: <b>{s['active_orders']}</b>\n"
            f"   ✅ Tayyor: <b>{s['done_orders']}</b>\n\n"
            f"💰 To'lovlar:\n"
            f"   ✅ Tasdiqlangan: <b>{s['confirmed_payments']}</b>\n"
            f"   ⏳ Kutilmoqda: <b>{s['pending_payments']}</b>"
        )
        await query.message.answer(text, parse_mode="HTML")

    elif action == "orders":
        orders = db.list_orders(20)
        if not orders:
            await query.message.answer("📭 Buyurtmalar yo'q.")
        else:
            status_map = {"new":"🆕 Yangi","confirmed":"✅ Tasdiqlangan","paid":"💰 To'langan",
                          "in_progress":"🔄 Jarayonda","done":"✅ Tayyor","rejected":"❌ Rad"}
            for o in orders:
                svc = db.get_service(o.get("service_id")) if o.get("service_id") else None
                text = (
                    f"📦 <b>#{o['id']}</b> — {svc['name'] if svc else '—'}\n"
                    f"👤 {o['name']} | 📞 {o['contact']}\n"
                    f"📝 {(o.get('details') or '—')[:100]}\n"
                    f"💰 {o.get('agreed_price') or '—'} | ⏰ {o.get('deadline') or '—'}\n"
                    f"Holat: <b>{status_map.get(o['status'], o['status'])}</b>"
                )
                await query.message.answer(text, reply_markup=admin_order_kb(o['id'], o['status'], o['user_id']), parse_mode="HTML")

    elif action == "clients":
        clients = db.all_clients_data()
        if not clients:
            await query.message.answer("👥 Mijozlar yo'q.")
        else:
            text = "👥 <b>Mijozlar:</b>\n\n"
            for c in clients[:20]:
                text += f"• {c.get('full_name') or '—'} (@{c.get('username') or '—'}) — {c.get('orders_count',0)} buyurtma\n"
            await query.message.answer(text, parse_mode="HTML")

    elif action == "payments":
        s = db.stats()
        await query.message.answer(
            f"💳 <b>To'lovlar</b>\n\n✅ Tasdiqlangan: <b>{s['confirmed_payments']}</b>\n⏳ Kutilmoqda: <b>{s['pending_payments']}</b>",
            parse_mode="HTML")

    elif action == "services":
        svcs = db.list_services()
        if not svcs: await query.message.answer("Xizmatlar yo'q.")
        else:
            text = "🛠 <b>Xizmatlar:</b>\n\n"
            for s in svcs: text += f"<b>#{s['id']}</b> — {s['name']} ({s['price']})\n"
            await query.message.answer(text, parse_mode="HTML")

    elif action == "broadcast":
        await state.set_state(BroadcastState.text)
        await query.message.answer("📢 Barcha foydalanuvchilarga xabarni yozing:")

    await query.answer()


@router.message(BroadcastState.text)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not _is_admin(message.from_user.id): return
    text = message.text or ""
    await state.clear()
    ok = fail = 0
    for uid in db.all_user_ids():
        try: await bot.send_message(uid, text, parse_mode="HTML"); ok += 1
        except: fail += 1
    await message.answer(f"✅ Yuborildi: {ok} | ❌ Xato: {fail}", reply_markup=main_menu_kb())
