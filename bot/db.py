"""
Postgres database helpers for the Telegram bot.
Mirrors the schema from telegram_bot.py but stored in Neon Postgres.
Uses bot_watches/bot_price_history tables to avoid conflicts with backend.
"""
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import psycopg2
from psycopg2.extras import RealDictCursor

# --------------------------------------------------------------------------- 
# Connection 
# ---------------------------------------------------------------------------

# SQLite fallback path for local dev (no Postgres needed)
SQLITE_FALLBACK_PATH = Path(__file__).parent / "watches.db"

def get_database_url() -> str:
    """Get DATABASE_URL from environment."""
    url = os.environ.get("DATABASE_URL")
    if url:
        # Normalize postgres:// -> postgresql:// for psycopg2
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://") and "sslmode=" not in url:
            url += "?sslmode=require"
        return url
    # For local dev, use SQLite
    return str(SQLITE_FALLBACK_PATH)

def get_connection():
    """Return a new psycopg2 connection (caller must close)."""
    url = get_database_url()
    if url.startswith("sqlite://") or url.endswith(".db"):
        # Local fallback - not used in prod
        import sqlite3
        conn = sqlite3.connect(url)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        return psycopg2.connect(url, cursor_factory=RealDictCursor)

# --------------------------------------------------------------------------- 
# Schema - Bot-specific tables (bot_watches, bot_price_history)
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS bot_watches (
    id          SERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    product_url TEXT   NOT NULL,
    product_name TEXT  NOT NULL DEFAULT 'Unknown product',
    target_price DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bot_price_history (
    id         SERIAL PRIMARY KEY,
    watch_id   INTEGER NOT NULL REFERENCES bot_watches(id) ON DELETE CASCADE,
    price      DOUBLE PRECISION NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bot_watches_user_id ON bot_watches(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_price_history_watch_id ON bot_price_history(watch_id, checked_at DESC);
"""

# --------------------------------------------------------------------------- 
# DB Initialization 
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create tables if they don't exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()

# --------------------------------------------------------------------------- 
# CRUD Helpers 
# ---------------------------------------------------------------------------

@contextmanager
def get_db_cursor(commit: bool = False):
    """Yield a cursor and optionally commit."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def add_watch(user_id: int, product_url: str, product_name: str) -> int:
    """Insert a new watch and return its ID."""
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO bot_watches (user_id, product_url, product_name, target_price, created_at)
            VALUES (%s, %s, %s, 0.0, NOW())
            RETURNING id
            """,
            (user_id, product_url, product_name),
        )
        row = cur.fetchone()
        return row['id'] if isinstance(row, dict) else row[0]

def list_watches(user_id: int = None):
    """Return list of watches. If user_id is None, return all watches."""
    with get_db_cursor() as cur:
        if user_id is not None:
            cur.execute(
                """
                SELECT id, product_name, product_url, target_price, user_id, created_at
                FROM bot_watches
                WHERE user_id = %s
                ORDER BY id
                """,
                (user_id,),
            )
        else:
            cur.execute(
                """
                SELECT id, product_name, product_url, target_price, user_id, created_at
                FROM bot_watches
                ORDER BY id
                """
            )
        return cur.fetchall()

def remove_watch(watch_id: int, user_id: int) -> bool:
    """Remove a watch if it belongs to the user. Returns True if deleted."""
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            DELETE FROM bot_watches
            WHERE id = %s AND user_id = %s
            """,
            (watch_id, user_id),
        )
        return cur.rowcount > 0

def set_target_price(watch_id: int, user_id: int, target_price: float) -> bool:
    """Set target price for a watch if it belongs to the user."""
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE bot_watches
            SET target_price = %s
            WHERE id = %s AND user_id = %s
            """,
            (target_price, watch_id, user_id),
        )
        return cur.rowcount > 0

def add_price_history(watch_id: int, price: float) -> None:
    """Insert a price check result."""
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO bot_price_history (watch_id, price, checked_at)
            VALUES (%s, %s, NOW())
            """,
            (watch_id, price),
        )

def get_recent_prices(watch_id: int, limit: int = 20):
    """Get recent price history for a watch (most recent first)."""
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT price, checked_at
            FROM bot_price_history
            WHERE watch_id = %s
            ORDER BY checked_at DESC
            LIMIT %s
            """,
            (watch_id, limit),
        )
        return cur.fetchall()

def get_latest_price(watch_id: int):
    """Get the most recent price for a watch."""
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT price, checked_at
            FROM bot_price_history
            WHERE watch_id = %s
            ORDER BY checked_at DESC
            LIMIT 1
            """,
            (watch_id,),
        )
        row = cur.fetchone()
        return row['price'] if row else None

# --------------------------------------------------------------------------- 
# Migration from SQLite (optional one-time) 
# ---------------------------------------------------------------------------

def migrate_from_sqlite(sqlite_path: str = None) -> None:
    """Migrate existing SQLite watches.db to Postgres. Safe to run multiple times."""
    if sqlite_path is None:
        sqlite_path = str(SQLITE_FALLBACK_PATH)
    
    import sqlite3
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = get_connection()
    
    try:
        # Ensure Postgres tables exist
        init_db()
        
        sqlite_cur = sqlite_conn.cursor()
        pg_cur = pg_conn.cursor()
        
        # Migrate watches
        sqlite_cur.execute("SELECT id, user_id, product_url, product_name, target_price, created_at FROM watches")
        watches = sqlite_cur.fetchall()
        for w in watches:
            pg_cur.execute(
                """
                INSERT INTO bot_watches (id, user_id, product_url, product_name, target_price, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (w['id'], w['user_id'], w['product_url'], w['product_name'], w['target_price'], w['created_at'])
            )
        
        # Migrate price_history
        sqlite_cur.execute("SELECT id, watch_id, price, checked_at FROM price_history")
        histories = sqlite_cur.fetchall()
        for h in histories:
            pg_cur.execute(
                """
                INSERT INTO bot_price_history (id, watch_id, price, checked_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (h['id'], h['watch_id'], h['price'], h['checked_at'])
            )
        
        pg_conn.commit()
        print(f"Migrated {len(watches)} watches and {len(histories)} price history records.")
    except Exception as e:
        pg_conn.rollback()
        raise e
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    # Allow running as script to migrate
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--migrate":
        sqlite_path = sys.argv[2] if len(sys.argv) > 2 else None
        migrate_from_sqlite(sqlite_path)
        print("Migration complete.")
    else:
        print("Usage: python bot/db.py --migrate [sqlite_path]")
