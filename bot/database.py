"""SQLite — users, services, orders, payments."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional
from .config import DB_PATH, logger

@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try: yield conn; conn.commit()
    except: conn.rollback(); raise
    finally: conn.close()

def _now(): return datetime.utcnow().isoformat(sep=" ", timespec="seconds")

def init_db():
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, language TEXT DEFAULT 'uz', source TEXT DEFAULT 'direct', created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, price TEXT NOT NULL, category TEXT DEFAULT 'general', active INTEGER DEFAULT 1, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, service_id INTEGER, name TEXT NOT NULL, contact TEXT NOT NULL, details TEXT, status TEXT NOT NULL DEFAULT 'new', agreed_price TEXT, deadline TEXT, deadline_at TEXT, work_started_at TEXT, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, user_id INTEGER NOT NULL, amount TEXT NOT NULL, receipt_file_id TEXT, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
        """)
        if c.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
            now = _now()
            seeds = [
                ("🤖 AI Avatar Video",
                 "AI texnologiyalari bilan professional avatar video yaratamiz. Rasmingiz asosida sun'iy intellekt jonli video tayyorlaydi — xuddi siz gapirayotgandek!\n\n✅ Reklama, kurs, ijtimoiy tarmoqlar uchun ideal\n✅ Har qanday tilda gapiradigan avatar\n✅ Tayyor ssenariy bilan ishlash mumkin",
                 "💰 1 daqiqagacha — 300 000 so'm\n📌 Undan ortiq — admin bilan kelishiladi", "video", now),
                ("📺 Reklama Videosi",
                 "Brendingiz uchun professional reklama videosi — diqqatni tortadigan, sotuvni oshiradigan kontent.\n\n✅ Ssenariy + montaj + musiqa — tayyor holda\n✅ Instagram, YouTube, Telegram uchun\n✅ A/B test uchun bir necha variant",
                 "💰 30 soniyagacha — 300 000 so'm\n💰 1 daqiqagacha — 500 000 so'm\n📌 Undan ortiq — admin bilan kelishiladi", "video", now),
                ("🎬 Intro & Outro",
                 "YouTube kanal yoki ijtimoiy tarmoqlar uchun professional kirish va chiqish videolari.\n\n✅ Brend ranglar, logo, musiqa — sizning uslubingizda\n✅ 2D va 3D animatsiya\n✅ Kanalingiz professional ko'rinadi",
                 "💰 Oddiy 2D — 150 000 so'm\n💰 3D animatsiyali — 300 000 so'm\n📌 Murakkab loyihalar — admin bilan kelishiladi", "video", now),
                ("📸 Foto Tayyorlash",
                 "Mahsulot rasmlari, portret, background o'zgartirish, sifat yaxshilash — AI yordamida.\n\n✅ Kamida 5 ta rasm tayyorlanadi\n✅ 2 tagacha bepul o'zgartirish\n✅ Tayyor rasmlar 24 soat ichida",
                 "💰 5 ta rasm — 30 000 so'm\n📌 Qo'shimcha rasm — 5 000 so'm", "image", now),
                ("✂ Video Tahrirlash",
                 "Professional montaj: kesish, color grading, effektlar, subtitr, musiqa.\n\n✅ YouTube, Reels, TikTok uchun\n✅ Tayyor loyiha fayli topshiriladi\n✅ 2 tagacha bepul tuzatish",
                 "💰 1 daqiqagacha — 150 000 so'm\n💰 3 daqiqagacha — 300 000 so'm\n💰 5+ daqiqa — 500 000 so'm dan\n📌 Murakkab — admin bilan kelishiladi", "video", now),
                ("🎨 Dizayn & Motion",
                 "Ijtimoiy tarmoqlar uchun dinamik grafika: animatsiyali postlar, storis, logo animatsiya.\n\n✅ Brendingiz hayotga kiradi\n✅ Instagram, Telegram, YouTube uchun\n✅ Tayyor fayllar barcha formatda",
                 "💰 1 ta animatsiya — 100 000 so'm\n💰 5 talik paket — 400 000 so'm\n💰 Logo animatsiya — 200 000 so'm\n📌 Maxsus — admin bilan kelishiladi", "image", now),
            ]
            c.executemany("INSERT INTO services (name,description,price,category,created_at) VALUES (?,?,?,?,?)", seeds)
        logger.info("DB ready: %s", DB_PATH)

def upsert_user(uid, username, full_name, source="direct"):
    with _conn() as c: c.execute("INSERT INTO users (user_id,username,full_name,source,created_at) VALUES (?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name", (uid, username, full_name, source, _now()))
def get_language(uid):
    with _conn() as c:
        r = c.execute("SELECT language FROM users WHERE user_id=?", (uid,)).fetchone()
        return (r["language"] or "uz") if r else "uz"
def all_user_ids():
    with _conn() as c: return [r["user_id"] for r in c.execute("SELECT user_id FROM users")]
def list_services():
    with _conn() as c: return c.execute("SELECT * FROM services WHERE active=1 ORDER BY id").fetchall()
def get_service(sid):
    with _conn() as c: return c.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone()
def create_order(uid, sid, name, contact, details):
    with _conn() as c: return c.execute("INSERT INTO orders (user_id,service_id,name,contact,details,status,created_at) VALUES (?,?,?,?,?,'new',?)", (uid, sid, name, contact, details, _now())).lastrowid
def get_order(oid):
    with _conn() as c:
        r = c.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
        return dict(r) if r else None
def update_order_status(oid, status):
    with _conn() as c:
        c.execute("UPDATE orders SET status=? WHERE id=?", (status, oid))
        r = c.execute("SELECT user_id FROM orders WHERE id=?", (oid,)).fetchone()
        return r["user_id"] if r else None
def update_order_price_deadline(oid, price, deadline, deadline_at=""):
    with _conn() as c: c.execute("UPDATE orders SET agreed_price=?, deadline=?, deadline_at=? WHERE id=?", (price, deadline, deadline_at, oid))
def set_work_started(oid):
    with _conn() as c: c.execute("UPDATE orders SET work_started_at=?, status='in_progress' WHERE id=?", (_now(), oid))
def list_orders(limit=20):
    with _conn() as c: return [dict(r) for r in c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
def get_user_orders(uid):
    with _conn() as c: return [dict(r) for r in c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()]
def create_payment(oid, uid, amount):
    with _conn() as c: return c.execute("INSERT INTO payments (order_id,user_id,amount,status,created_at) VALUES (?,?,?,'pending',?)", (oid, uid, amount, _now())).lastrowid
def set_payment_receipt(pid, file_id):
    with _conn() as c: c.execute("UPDATE payments SET receipt_file_id=?, status='checking' WHERE id=?", (file_id, pid))
def update_payment_status(pid, status):
    with _conn() as c:
        c.execute("UPDATE payments SET status=? WHERE id=?", (status, pid))
        r = c.execute("SELECT user_id FROM payments WHERE id=?", (pid,)).fetchone()
        return r["user_id"] if r else None
def get_payment(pid):
    with _conn() as c:
        r = c.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone()
        return dict(r) if r else None
def stats():
    with _conn() as c:
        today, month = datetime.utcnow().strftime('%Y-%m-%d'), datetime.utcnow().strftime('%Y-%m')
        return {"total_users": c.execute("SELECT COUNT(*) FROM users").fetchone()[0], "today_users": c.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (today+'%',)).fetchone()[0], "total_orders": c.execute("SELECT COUNT(*) FROM orders").fetchone()[0], "today_orders": c.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (today+'%',)).fetchone()[0], "month_orders": c.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (month+'%',)).fetchone()[0], "new_orders": c.execute("SELECT COUNT(*) FROM orders WHERE status='new'").fetchone()[0], "active_orders": c.execute("SELECT COUNT(*) FROM orders WHERE status IN ('confirmed','in_progress','paid')").fetchone()[0], "done_orders": c.execute("SELECT COUNT(*) FROM orders WHERE status='done'").fetchone()[0], "confirmed_payments": c.execute("SELECT COUNT(*) FROM payments WHERE status='confirmed'").fetchone()[0], "pending_payments": c.execute("SELECT COUNT(*) FROM payments WHERE status IN ('pending','checking')").fetchone()[0]}
def all_orders_data():
    with _conn() as c: return [dict(r) for r in c.execute("SELECT o.*, s.name as svc_name, u.username, u.full_name as user_fullname FROM orders o LEFT JOIN services s ON o.service_id=s.id LEFT JOIN users u ON o.user_id=u.user_id ORDER BY o.id DESC").fetchall()]
def all_clients_data():
    with _conn() as c: return [dict(r) for r in c.execute("SELECT u.*, (SELECT COUNT(*) FROM orders o WHERE o.user_id=u.user_id) as orders_count, (SELECT MAX(created_at) FROM orders o WHERE o.user_id=u.user_id) as last_order FROM users u ORDER BY u.created_at DESC").fetchall()]
