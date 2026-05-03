"""Keyboards."""
import os
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def _inline(*rows): return InlineKeyboardMarkup(inline_keyboard=list(rows))
def _btn(t, cb): return InlineKeyboardButton(text=t, callback_data=cb)
def _url(t, u): return InlineKeyboardButton(text=t, url=u)

def main_menu_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛠 Xizmatlar"), KeyboardButton(text="🛒 Buyurtma")],
        [KeyboardButton(text="📦 Zakazlarim"), KeyboardButton(text="🖼 Portfolio")],
        [KeyboardButton(text="ℹ️ Biz haqimizda"), KeyboardButton(text="📞 Aloqa")],
    ], resize_keyboard=True)

def cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)

def services_kb(services):
    rows = []
    row = []
    for s in services:
        row.append(_btn(s["name"], f"svc:{s['id']}"))
        if len(row) == 2: rows.append(row); row = []
    if row: rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)

def service_detail_kb(sid):
    return _inline(
        [_btn("🛒 Buyurtma berish", f"order:{sid}")],
        [_url("💬 Admin bilan kelishish", "https://t.me/qaxxarov_98")],
        [_btn("◀️ Ortga", "svc:back")])

def admin_panel_kb():
    aid = os.environ.get("ADMIN_ID", "")
    web = f"https://asmo-bot.onrender.com/admin?token={aid}"
    return _inline(
        [_url("🌐 Web Admin Panel", web)],
        [_btn("📊 Statistika", "admin:stats"), _btn("👥 Mijozlar", "admin:clients")],
        [_btn("📦 Buyurtmalar", "admin:orders"), _btn("💳 To'lovlar", "admin:payments")],
        [_btn("🛠 Xizmatlar", "admin:services"), _btn("📢 Broadcast", "admin:broadcast")])

def admin_order_kb(oid, status, uid):
    b = []
    if status == "new": b.append([_btn("✅ Qabul + Narx", f"ord:setprice:{oid}"), _btn("❌ Rad", f"ord:reject:{oid}")])
    elif status in ("confirmed", "paid"): b.append([_btn("🔄 Ishni boshlash", f"ord:startwork:{oid}")])
    elif status == "in_progress": b.append([_btn("✅ Tayyor!", f"ord:done:{oid}")])
    b.append([_url("💬 Chat", f"tg://user?id={uid}")])
    return InlineKeyboardMarkup(inline_keyboard=b)

def payment_confirm_kb(oid):
    return _inline(
        [_btn("💳 To'ladim — chek yuborish", f"pay:start:{oid}")],
        [_url("💬 Admin bilan gaplashish", "https://t.me/qaxxarov_98")])
