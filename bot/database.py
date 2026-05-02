"""SQLite data layer — users, services, orders, payments, requests."""

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


def init_db() -> None:
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT,
                full_name  TEXT,
                language   TEXT DEFAULT 'uz',
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
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                service_id INTEGER,
                name       TEXT NOT NULL,
                contact    TEXT NOT NULL,
                details    TEXT,
                status     TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL
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

            CREATE TABLE IF NOT EXISTS client_requests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                type        TEXT NOT NULL,
                summary     TEXT,
                order_id    INTEGER,
                status      TEXT NOT NULL DEFAULT 'open',
                created_at  TEXT NOT NULL,
                resolved_at TEXT
            );
        """)

        # Seed default services if empty
        cur = c.execute("SELECT COUNT(*) AS n FROM services")
        if cur.fetchone()["n"] == 0:
            now = _now()
            seeds = [
                ("🤖 AI Avatar Video",
                 "AI texnologiyalari yordamida professional avatar videolar yaratish.",
                 "Narx kelishiladi", "video", now),
                ("📺 Reklama Videosi",
                 "30-60 soniyali professional brend reklama videolari.",
                 "Narx kelishiladi", "video", now),
                ("🎬 Intro & Outro",
                 "YouTube va social media uchun professional intro va outro.",
                 "Narx kelishiladi", "video", now),
                ("📸 Foto Tayyorlash",
                 "AI yordamida foto sifatini yaxshilash va background o'zgartirish.",
                 "Narx kelishiladi", "image", now),
                ("✂ Video Tahrirlash",
                 "Professional montaj, color grading va effektlar.",
                 "Narx kelishiladi", "video", now),
                ("🎨 Dizayn & Motion",
                 "Social media uchun dinamik grafika va motion graphics.",
                 "Narx kelishiladi", "image", now),
            ]
            c.executemany(
                "INSERT INTO services (name,description,price,category,created_at) VALUES (?,?,?,?,?)",
                seeds,
            )
        logger.info("DB ready: %s", DB_PATH)


def _now() -> str:
    return datetime.utcnow().isoformat(sep=" ", timespec="seconds")


# ── Users ──────────────────────────────────────────────────────────────────

def upsert_user(user_id: int, username: Optional[str], full_name: str) -> None:
    with _conn() as c:
        c.execute(
            """INSERT INTO users (user_id,username,full_name,created_at)
               VALUES (?,?,?,?)
               ON CONFLICT(user_id) DO UPDATE SET
                 username=excluded.username, full_name=excluded.full_name""",
            (user_id, username, full_name, _now()),
        )


def set_language(user_id: int, lang: str) -> None:
    with _conn() as c:
        c.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))


def get_language(user_id: int) -> str:
    with _conn() as c:
        row = c.execute("SELECT language FROM users WHERE user_id=?", (user_id,)).fetchone()
        return (row["language"] or "uz") if row else "uz"


def get_user(user_id: int):
    with _conn() as c:
        return c.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()


def all_user_ids() -> list:
    with _conn() as c:
        return [r["user_id"] for r in c.execute("SELECT user_id FROM users")]


def list_clients() -> list:
    with _conn() as c:
        return c.execute("""
            SELECT u.*,
              (SELECT COUNT(*) FROM orders o WHERE o.user_id=u.user_id) AS orders_count,
              (SELECT COUNT(*) FROM client_requests r
               WHERE r.user_id=u.user_id AND r.status='open') AS open_count
            FROM users u
            WHERE EXISTS(SELECT 1 FROM orders o WHERE o.user_id=u.user_id)
               OR EXISTS(SELECT 1 FROM client_requests r WHERE r.user_id=u.user_id)
            ORDER BY open_count DESC, u.user_id DESC
        """).fetchall()


# ── Services ───────────────────────────────────────────────────────────────

def list_services() -> list:
    with _conn() as c:
        return c.execute("SELECT * FROM services WHERE active=1 ORDER BY id").fetchall()


def get_service(sid: int):
    with _conn() as c:
        return c.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone()


def add_service(name: str, description: str, price: str, category: str = "general") -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO services (name,description,price,category,created_at) VALUES (?,?,?,?,?)",
            (name, description, price, category, _now()),
        )
        return cur.lastrowid


def delete_service(sid: int) -> bool:
    with _conn() as c:
        cur = c.execute("UPDATE services SET active=0 WHERE id=?", (sid,))
        return cur.rowcount > 0


# ── Orders ─────────────────────────────────────────────────────────────────

def create_order(user_id: int, service_id: Optional[int],
                 name: str, contact: str, details: str) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO orders (user_id,service_id,name,contact,details,status,created_at) "
            "VALUES (?,?,?,?,?,'new',?)",
            (user_id, service_id, name, contact, details, _now()),
        )
        return cur.lastrowid


def get_order(order_id: int):
    with _conn() as c:
        return c.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()


def update_order_status(order_id: int, status: str) -> Optional[int]:
    with _conn() as c:
        c.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        row = c.execute("SELECT user_id FROM orders WHERE id=?", (order_id,)).fetchone()
        return row["user_id"] if row else None


def list_orders(limit: int = 20) -> list:
    with _conn() as c:
        return c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def get_user_orders(user_id: int) -> list:
    with _conn() as c:
        return c.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (user_id,)
        ).fetchall()


# ── Payments ───────────────────────────────────────────────────────────────

def create_payment(order_id: int, user_id: int, amount: str) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO payments (order_id,user_id,amount,status,created_at) VALUES (?,?,?,'pending',?)",
            (order_id, user_id, amount, _now()),
        )
        return cur.lastrowid


def set_payment_receipt(payment_id: int, file_id: str) -> None:
    with _conn() as c:
        c.execute(
            "UPDATE payments SET receipt_file_id=?, status='checking' WHERE id=?",
            (file_id, payment_id),
        )


def update_payment_status(payment_id: int, status: str) -> Optional[int]:
    with _conn() as c:
        c.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
        row = c.execute("SELECT user_id FROM payments WHERE id=?", (payment_id,)).fetchone()
        return row["user_id"] if row else None


def get_payment(payment_id: int):
    with _conn() as c:
        return c.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()


def get_order_payment(order_id: int):
    with _conn() as c:
        return c.execute(
            "SELECT * FROM payments WHERE order_id=? ORDER BY id DESC LIMIT 1", (order_id,)
        ).fetchone()


# ── Requests ───────────────────────────────────────────────────────────────

def add_request(user_id: int, type_: str,
                summary: str = "", order_id: Optional[int] = None) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO client_requests (user_id,type,summary,order_id,status,created_at) "
            "VALUES (?,?,?,?,'open',?)",
            (user_id, type_, summary, order_id, _now()),
        )
        return cur.lastrowid


def set_request_status(req_id: int, status: str) -> Optional[int]:
    with _conn() as c:
        resolved = _now() if status == "resolved" else None
        c.execute(
            "UPDATE client_requests SET status=?,resolved_at=? WHERE id=?",
            (status, resolved, req_id),
        )
        row = c.execute("SELECT user_id FROM client_requests WHERE id=?", (req_id,)).fetchone()
        return row["user_id"] if row else None


def resolve_user_open_requests(user_id: int) -> int:
    with _conn() as c:
        cur = c.execute(
            "UPDATE client_requests SET status='resolved',resolved_at=? "
            "WHERE user_id=? AND status='open'",
            (_now(), user_id),
        )
        return cur.rowcount


def get_user_requests(user_id: int) -> list:
    with _conn() as c:
        return c.execute(
            "SELECT * FROM client_requests WHERE user_id=? ORDER BY id DESC", (user_id,)
        ).fetchall()


# ── Stats ──────────────────────────────────────────────────────────────────

def stats() -> dict:
    with _conn() as c:
        return {
            "users":            c.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "orders":           c.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "services":         c.execute("SELECT COUNT(*) FROM services WHERE active=1").fetchone()[0],
            "payments_ok":      c.execute("SELECT COUNT(*) FROM payments WHERE status='confirmed'").fetchone()[0],
            "payments_pending": c.execute("SELECT COUNT(*) FROM payments WHERE status='checking'").fetchone()[0],
        }
