"""Keyboards — all bot keyboards."""

import os
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)

def _inline(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

def _btn(text, cb) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=cb)

def _url(text, url) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


# ── Main menu ──────────────────────────────────────────────────────────────
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛠 Xizmatlar"), KeyboardButton(text="🛒 Buyurtma")],
        [KeyboardButton(text="📦 Zakazlarim"), KeyboardButton(text="🖼 Portfolio")],
        [KeyboardButton(text="ℹ️ Biz haqimizda"), KeyboardButton(text="📞 Aloqa")],
    ], resize_keyboard=True)

def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True)

def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ── Services ───────────────────────────────────────────────────────────────
def services_kb(services) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for s in services:
        row.append(_btn(s["name"], f"svc:{s['id']}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)

def service_detail_kb(sid: int) -> InlineKeyboardMarkup:
    return _inline(
        [_btn("🛒 Buyurtma berish", f"order:{sid}")],
        [_btn("◀️ Ortga", "svc:back")])


# ── Admin ──────────────────────────────────────────────────────────────────
def admin_panel_kb() -> InlineKeyboardMarkup:
    admin_id = os.environ.get("ADMIN_ID", "")
    web = f"https://asmo-bot.onrender.com/admin?token={admin_id}"
    return _inline(
        [_url("🌐 Web Admin Panel", web)],
        [_btn("📊 Statistika", "admin:stats"), _btn("👥 Mijozlar", "admin:clients")],
        [_btn("📦 Buyurtmalar", "admin:orders"), _btn("💳 To'lovlar", "admin:payments")],
        [_btn("🛠 Xizmatlar", "admin:services"), _btn("📢 Broadcast", "admin:broadcast")],
    )

def admin_order_kb(order_id: int, status: str, user_id: int) -> InlineKeyboardMarkup:
    buttons = []
    if status == "new":
        buttons.append([_btn("✅ Qabul + Narx", f"ord:setprice:{order_id}"),
                        _btn("❌ Rad", f"ord:reject:{order_id}")])
    elif status in ("confirmed", "paid"):
        buttons.append([_btn("🔄 Ishni boshlash", f"ord:startwork:{order_id}")])
    elif status == "in_progress":
        buttons.append([_btn("✅ Tayyor!", f"ord:done:{order_id}")])
    buttons.append([_url("💬 Chat", f"tg://user?id={user_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def payment_confirm_kb(order_id: int) -> InlineKeyboardMarkup:
    return _inline(
        [_btn("💳 To'ladim — chek yuborish", f"pay:start:{order_id}")],
        [_url("💬 Admin bilan gaplashish", "https://t.me/qaxxarov_98")])
