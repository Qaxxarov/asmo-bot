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
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _now() -> str:
    return datetime.utcnow().isoformat(sep=" ", timespec="seconds")


def init_db() -> None:
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT,
                full_name  TEXT,
                language   TEXT DEFAULT 'uz',
                source     TEXT DEFAULT 'direct',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS services (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT NOT NULL,
                price       TEXT NOT NULL,
                category    TEXT DEFAULT 'general',
                active      INTEGER DEFAULT 1,
                created_at  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS orders (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                service_id   INTEGER,
                name         TEXT NOT NULL,
                contact      TEXT NOT NULL,
                details      TEXT,
                status       TEXT NOT NULL DEFAULT 'new',
                agreed_price TEXT,
                deadline     TEXT,
                created_at   TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS payments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id        INTEGER NOT NULL,
                user_id         INTEGER NOT NULL,
                amount          TEXT NOT NULL,
                receipt_file_id TEXT,
                status          TEXT NOT NULL DEFAULT 'pending',
                created_at      TEXT NOT NULL
            );
        """)
        cur = c.execute("SELECT COUNT(*) AS n FROM services")
        if cur.fetchone()["n"] == 0:
            now = _now()
            seeds = [
                ("🤖 AI Avatar Video", "AI texnologiyalari yordamida professional avatar videolar.", "Narx kelishiladi", "video", now),
                ("📺 Reklama Videosi", "30-60 soniyali professional brend reklama videolari.", "Narx kelishiladi", "video", now),
                ("🎬 Intro & Outro", "YouTube va social media uchun professional intro va outro.", "Narx kelishiladi", "video", now),
                ("📸 Foto Tayyorlash", "AI yordamida foto sifatini yaxshilash va background o'zgartirish.", "Narx kelishiladi", "image", now),
                ("✂ Video Tahrirlash", "Professional montaj, color grading va effektlar.", "Narx kelishiladi", "video", now),
                ("🎨 Dizayn & Motion", "Social media uchun dinamik grafika va motion graphics.", "Narx kelishiladi", "image", now),
            ]
            c.executemany("INSERT INTO services (name,description,price,category,created_at) VALUES (?,?,?,?,?)", seeds)
        logger.info("DB ready: %s", DB_PATH)


# ── Users ──────────────────────────────────────────────────────────────────
def upsert_user(user_id: int, username: Optional[str], full_name: str, source: str = "direct") -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO users (user_id,username,full_name,source,created_at) VALUES (?,?,?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name",
            (user_id, username, full_name, source, _now()))

def get_language(user_id: int) -> str:
    with _conn() as c:
        row = c.execute("SELECT language FROM users WHERE user_id=?", (user_id,)).fetchone()
        return (row["language"] or "uz") if row else "uz"

def set_language(user_id: int, lang: str) -> None:
    with _conn() as c:
        c.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))

def get_user(user_id: int):
    with _conn() as c:
        return c.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()

def all_user_ids() -> list:
    with _conn() as c:
        return [r["user_id"] for r in c.execute("SELECT user_id FROM users")]


# ── Services ───────────────────────────────────────────────────────────────
def list_services() -> list:
    with _conn() as c:
        return c.execute("SELECT * FROM services WHERE active=1 ORDER BY id").fetchall()

def get_service(sid: int):
    with _conn() as c:
        return c.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone()

def add_service(name: str, description: str, price: str, category: str = "general") -> int:
    with _conn() as c:
        cur = c.execute("INSERT INTO services (name,description,price,category,created_at) VALUES (?,?,?,?,?)",
                        (name, description, price, category, _now()))
        return cur.lastrowid

def delete_service(sid: int) -> bool:
    with _conn() as c:
        return c.execute("UPDATE services SET active=0 WHERE id=?", (sid,)).rowcount > 0


# ── Orders ─────────────────────────────────────────────────────────────────
def create_order(user_id: int, service_id: Optional[int], name: str, contact: str, details: str) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO orders (user_id,service_id,name,contact,details,status,created_at) VALUES (?,?,?,?,?,'new',?)",
            (user_id, service_id, name, contact, details, _now()))
        return cur.lastrowid

def get_order(order_id: int):
    with _conn() as c:
        return c.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

def update_order_status(order_id: int, status: str) -> Optional[int]:
    with _conn() as c:
        c.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        row = c.execute("SELECT user_id FROM orders WHERE id=?", (order_id,)).fetchone()
        return row["user_id"] if row else None

def update_order_price_deadline(order_id: int, price: str, deadline: str) -> None:
    with _conn() as c:
        c.execute("UPDATE orders SET agreed_price=?, deadline=? WHERE id=?", (price, deadline, order_id))

def list_orders(limit: int = 20) -> list:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

def get_user_orders(user_id: int) -> list:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()]


# ── Payments ───────────────────────────────────────────────────────────────
def create_payment(order_id: int, user_id: int, amount: str) -> int:
    with _conn() as c:
        cur = c.execute("INSERT INTO payments (order_id,user_id,amount,status,created_at) VALUES (?,?,?,'pending',?)",
                        (order_id, user_id, amount, _now()))
        return cur.lastrowid

def set_payment_receipt(payment_id: int, file_id: str) -> None:
    with _conn() as c:
        c.execute("UPDATE payments SET receipt_file_id=?, status='checking' WHERE id=?", (file_id, payment_id))

def update_payment_status(payment_id: int, status: str) -> Optional[int]:
    with _conn() as c:
        c.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
        row = c.execute("SELECT user_id FROM payments WHERE id=?", (payment_id,)).fetchone()
        return row["user_id"] if row else None

def get_payment(payment_id: int):
    with _conn() as c:
        return c.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()


# ── Stats ──────────────────────────────────────────────────────────────────
def stats() -> dict:
    with _conn() as c:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        month = datetime.utcnow().strftime('%Y-%m')
        return {
            "total_users":    c.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "today_users":    c.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE ?", (today+'%',)).fetchone()[0],
            "total_orders":   c.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "today_orders":   c.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (today+'%',)).fetchone()[0],
            "month_orders":   c.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (month+'%',)).fetchone()[0],
            "new_orders":     c.execute("SELECT COUNT(*) FROM orders WHERE status='new'").fetchone()[0],
            "active_orders":  c.execute("SELECT COUNT(*) FROM orders WHERE status IN ('confirmed','in_progress')").fetchone()[0],
            "done_orders":    c.execute("SELECT COUNT(*) FROM orders WHERE status='done'").fetchone()[0],
            "confirmed_payments": c.execute("SELECT COUNT(*) FROM payments WHERE status='confirmed'").fetchone()[0],
            "pending_payments":   c.execute("SELECT COUNT(*) FROM payments WHERE status IN ('pending','checking')").fetchone()[0],
        }

def all_orders_data() -> list:
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT o.*, s.name as svc_name, u.username, u.full_name as user_fullname "
            "FROM orders o LEFT JOIN services s ON o.service_id=s.id "
            "LEFT JOIN users u ON o.user_id=u.user_id ORDER BY o.id DESC").fetchall()]

def all_clients_data() -> list:
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT u.*, (SELECT COUNT(*) FROM orders o WHERE o.user_id=u.user_id) as orders_count, "
            "(SELECT MAX(created_at) FROM orders o WHERE o.user_id=u.user_id) as last_order "
            "FROM users u ORDER BY u.created_at DESC").fetchall()]
