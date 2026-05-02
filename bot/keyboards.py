"""Keyboards — clean 2-per-row layout, consistent emoji style."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from .locales import TEXTS, t


# ── Helpers ────────────────────────────────────────────────────────────────

def _inline(*rows: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

def _btn(text: str, cb: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=cb)

def _url_btn(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


# ── Language ───────────────────────────────────────────────────────────────

def language_kb() -> InlineKeyboardMarkup:
    return _inline(
        [_btn("🇺🇿 O'zbekcha", "lang:uz"),
         _btn("🇷🇺 Русский",   "lang:ru")],
    )


# ── Main menu ──────────────────────────────────────────────────────────────

def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_services")),
             KeyboardButton(text=t(lang, "menu_order"))],
            [KeyboardButton(text=t(lang, "menu_portfolio")),
             KeyboardButton(text=t(lang, "menu_about"))],
            [KeyboardButton(text=t(lang, "menu_contact")),
             KeyboardButton(text=t(lang, "menu_change_lang"))],
        ],
        resize_keyboard=True,
    )


# ── Services ───────────────────────────────────────────────────────────────

def services_kb(services, lang: str) -> InlineKeyboardMarkup:
    """2 services per row."""
    rows = []
    row = []
    for svc in services:
        row.append(_btn(svc["name"], f"svc:{svc['id']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def service_detail_kb(service_id: int, lang: str) -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "btn_order_this"), f"order:{service_id}")],
        [_btn(t(lang, "btn_back"),       "svc:back")],
    )


# ── Order / Cancel ─────────────────────────────────────────────────────────

def cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "btn_cancel"))]],
        resize_keyboard=True,
    )

def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ── Payment ────────────────────────────────────────────────────────────────

def payment_kb(lang: str) -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "btn_paid"),      "pay:receipt")],
        [_btn(t(lang, "btn_pay_later"), "pay:later")],
    )

def admin_payment_kb(payment_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    return _inline(
        [_btn("✅ Tasdiqlash" if lang == "uz" else "✅ Подтвердить",
              f"pmt:confirm:{payment_id}"),
         _btn("❌ Rad etish" if lang == "uz" else "❌ Отклонить",
              f"pmt:reject:{payment_id}")],
    )


# ── AI quick-actions ───────────────────────────────────────────────────────

def quick_order_kb(lang: str) -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "btn_order_now"),  "ai:order"),
         _btn(t(lang, "btn_call_admin"), "ai:call_admin")],
    )


# ── Admin panel ────────────────────────────────────────────────────────────

def admin_panel_kb(lang: str) -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "admin_stats"),    "admin:stats"),
         _btn(t(lang, "admin_clients"),  "admin:clients")],
        [_btn(t(lang, "admin_orders"),   "admin:orders"),
         _btn(t(lang, "admin_payments"), "admin:payments")],
        [_btn(t(lang, "admin_services"), "admin:services"),
         _btn(t(lang, "admin_broadcast"),"admin:broadcast")],
    )

def admin_services_kb(lang: str) -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "admin_add_service"), "admin:svc_add"),
         _btn(t(lang, "admin_del_service"), "admin:svc_del")],
    )

def order_review_kb(order_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "btn_approve"), f"ord:approve:{order_id}"),
         _btn(t(lang, "btn_reject"),  f"ord:reject:{order_id}")],
    )

def admin_request_kb(req_id: int, user_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "btn_reply"),   f"adm:reply:{user_id}"),
         _url_btn(t(lang, "btn_open_chat"), f"tg://user?id={user_id}")],
        [_btn(t(lang, "btn_resolve"), f"adm:rreq:{req_id}")],
    )

def admin_clients_kb(clients, lang: str) -> InlineKeyboardMarkup:
    rows = []
    for c in clients:
        badge = f" 🔴{c['open_count']}" if c["open_count"] else ""
        name = (c["full_name"] or
                (f"@{c['username']}" if c["username"] else str(c["user_id"])))
        rows.append([_btn(f"{name}{badge}", f"adm:client:{c['user_id']}")])
    rows.append([_btn(t(lang, "btn_back"), "adm:clients_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admin_client_detail_kb(user_id: int, lang: str) -> InlineKeyboardMarkup:
    return _inline(
        [_btn(t(lang, "btn_reply"),       f"adm:reply:{user_id}"),
         _url_btn(t(lang, "btn_open_chat"), f"tg://user?id={user_id}")],
        [_btn(t(lang, "btn_resolve_all"), f"adm:resolve_all:{user_id}")],
        [_btn(t(lang, "btn_back"),        "admin:clients")],
    )


# ── Utility ────────────────────────────────────────────────────────────────

def all_menu_values(key: str) -> set:
    """Return button texts for all languages (for message filter matching)."""
    return {TEXTS[l][key] for l in TEXTS if key in TEXTS[l]}
