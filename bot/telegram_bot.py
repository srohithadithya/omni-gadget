"""
AIDE-OS Telegram Price-Drop Bot.

Tracks product prices on Amazon / Flipkart and notifies users when prices fall.
Standalone process with its own SQLite database (bot/watches.db).

Usage:
    python telegram_bot.py          # run directly
    from telegram_bot import main   # call from main.py
"""

import logging
import os
import re
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from price_check import PriceChecker

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).parent / ".env")

TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DB_PATH: Path = Path(__file__).parent / "watches.db"

logger = logging.getLogger("aide_os.telegram_bot")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS watches (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    product_url TEXT    NOT NULL,
    product_name TEXT   NOT NULL DEFAULT 'Unknown product',
    target_price REAL  NOT NULL DEFAULT 0.0,
    created_at  TEXT   NOT NULL
);

CREATE TABLE IF NOT EXISTS price_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    watch_id   INTEGER NOT NULL,
    price      REAL    NOT NULL,
    checked_at TEXT    NOT NULL,
    FOREIGN KEY (watch_id) REFERENCES watches(id) ON DELETE CASCADE
);
"""


def init_db() -> None:
    """Create the SQLite database and tables if they don't already exist."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    logger.info("Database initialised at %s", DB_PATH)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a short-lived SQLite connection with WAL mode and row_factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# URL / product helpers
# ---------------------------------------------------------------------------

def extract_product_name(url: str) -> str:
    """Best-effort product name extraction from an e-commerce URL.

    Currently returns a human-readable placeholder derived from the URL
    hostname and path.  A future version can scrape the <title> tag.
    """
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").replace("www.", "")
    path_parts = [p for p in parsed.path.split("/") if p and p not in ("dp", "gp", "product")]
    slug = path_parts[-1] if path_parts else "product"
    slug = slug.replace("-", " ").replace("_", " ")[:60]
    return f"{hostname} – {slug}"


def detect_platform(url: str) -> str:
    """Return 'amazon', 'flipkart', or 'unknown'."""
    lower = url.lower()
    if "amazon" in lower:
        return "amazon"
    if "flipkart" in lower:
        return "flipkart"
    return "unknown"


def is_valid_url(text: str) -> bool:
    """Return True if *text* looks like a well-formed HTTP(S) URL."""
    try:
        result = urlparse(text)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start — greet the user and explain the bot."""
    welcome = (
        "👋 Welcome to **AIDE-OS Price Tracker**!\n\n"
        "I monitor product prices on Amazon and Flipkart and alert you "
        "when they drop.\n\n"
        "📦 **Commands**\n"
        "• /track <url> — Start tracking a product\n"
        "• /list — Show all your tracked products\n"
        "• /setprice <id> <price> — Set a target price alert\n"
        "• /remove <id> — Stop tracking a product\n"
        "• /check — Run a price check now\n\n"
        "Get started by pasting a product URL with /track!"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")  # type: ignore[union-attr]


async def cmd_track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /track <url> — add a product to the watch list."""
    if not context.args:
        await update.message.reply_text(  # type: ignore[union-attr]
            "Usage: /track <product_url>\n"
            "Example: /track https://www.amazon.in/dp/B0EXAMPLE"
        )
        return

    url = context.args[0].strip()
    if not is_valid_url(url):
        await update.message.reply_text("❌ That doesn't look like a valid URL. Please try again.")  # type: ignore[union-attr]
        return

    user_id: int = update.effective_user.id  # type: ignore[union-attr]
    product_name = extract_product_name(url)
    now = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        conn.execute(
            "INSERT INTO watches (user_id, product_url, product_name, target_price, created_at) "
            "VALUES (?, ?, ?, 0.0, ?)",
            (user_id, url, product_name, now),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id FROM watches WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        watch_id = row["id"] if row else "?"

    await update.message.reply_text(  # type: ignore[union-attr]
        f"✅ Now tracking!\n\n"
        f"🆔 Watch ID: {watch_id}\n"
        f"📦 {product_name}\n"
        f"🔗 {url}\n\n"
        f"Use /setprice {watch_id} <amount> to set a price alert."
    )


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list — show all products tracked by this user."""
    user_id: int = update.effective_user.id  # type: ignore[union-attr]

    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, product_name, product_url, target_price FROM watches WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()

    if not rows:
        await update.message.reply_text("📭 You aren't tracking any products yet.\nUse /track <url> to start.")  # type: ignore[union-attr]
        return

    lines = ["📋 **Your Tracked Products**\n"]
    for r in rows:
        target_str = f"₹{r['target_price']:.2f}" if r["target_price"] > 0 else "Any drop"
        lines.append(
            f"**#{r['id']}** — {r['product_name']}\n"
            f"   Target: {target_str}\n"
            f"   {r['product_url']}\n"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")  # type: ignore[union-attr]


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /remove <id> — delete a watch entry."""
    if not context.args:
        await update.message.reply_text("Usage: /remove <watch_id>")  # type: ignore[union-attr]
        return

    try:
        watch_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Watch ID must be a number.")  # type: ignore[union-attr]
        return

    user_id: int = update.effective_user.id  # type: ignore[union-attr]

    with get_db() as conn:
        row = conn.execute(
            "SELECT id, product_name FROM watches WHERE id = ? AND user_id = ?",
            (watch_id, user_id),
        ).fetchone()
        if not row:
            await update.message.reply_text("❌ Watch not found or doesn't belong to you.")  # type: ignore[union-attr]
            return
        conn.execute("DELETE FROM price_history WHERE watch_id = ?", (watch_id,))
        conn.execute("DELETE FROM watches WHERE id = ?", (watch_id,))
        conn.commit()

    await update.message.reply_text(f"🗑 Removed **{row['product_name']}** (#{watch_id}).", parse_mode="Markdown")  # type: ignore[union-attr]


async def cmd_setprice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setprice <id> <price> — set target price for alerts."""
    if len(context.args) < 2:  # type: ignore[arg-type]
        await update.message.reply_text("Usage: /setprice <watch_id> <target_price>")  # type: ignore[union-attr]
        return

    try:
        watch_id = int(context.args[0])
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Both arguments must be numbers.")  # type: ignore[union-attr]
        return

    if target_price <= 0:
        await update.message.reply_text("❌ Target price must be greater than 0.")  # type: ignore[union-attr]
        return

    user_id: int = update.effective_user.id  # type: ignore[union-attr]

    with get_db() as conn:
        row = conn.execute(
            "SELECT id, product_name FROM watches WHERE id = ? AND user_id = ?",
            (watch_id, user_id),
        ).fetchone()
        if not row:
            await update.message.reply_text("❌ Watch not found or doesn't belong to you.")  # type: ignore[union-attr]
            return
        conn.execute("UPDATE watches SET target_price = ? WHERE id = ?", (target_price, watch_id))
        conn.commit()

    await update.message.reply_text(  # type: ignore[union-attr]
        f"🎯 Target price for **{row['product_name']}** set to ₹{target_price:.2f}\n"
        f"I'll notify you when the price drops below this.",
        parse_mode="Markdown",
    )


async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /check — run a price check on ALL products for this user."""
    user_id: int = update.effective_user.id  # type: ignore[union-attr]

    with get_db() as conn:
        rows = conn.execute(
            "SELECT id FROM watches WHERE user_id = ?", (user_id,)
        ).fetchall()

    if not rows:
        await update.message.reply_text("📭 Nothing to check. Add products with /track first.")  # type: ignore[union-attr]
        return

    await update.message.reply_text("⏳ Checking prices…")  # type: ignore[union-attr]

    checker = PriceChecker(DB_PATH)
    try:
        results = checker.check_all_watches()
    except Exception:
        logger.exception("Price check failed")
        await update.message.reply_text("❌ Price check failed. Check logs for details.")  # type: ignore[union-attr]
        return

    user_results = [r for r in results if r.user_id == user_id]
    if not user_results:
        await update.message.reply_text("✅ Check complete. No results to report.")  # type: ignore[union-attr]
        return

    lines = ["📊 **Price Check Results**\n"]
    for r in user_results:
        arrow = "📉" if r.dropped else "➡️"
        lines.append(
            f"{arrow} **#{r.watch_id}** {r.product_name}\n"
            f"   Current: ₹{r.current_price:.2f}  |  Previous: ₹{r.previous_price:.2f}\n"
        )
        if r.dropped:
            lines.append(f"   🔔 Price dropped!\n")
        if r.meets_target:
            lines.append(
                f"   🎯 Below target price of ₹{r.target_price:.2f}!\n"
            )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")  # type: ignore[union-attr]


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help — show available commands."""
    await update.message.reply_text(  # type: ignore[union-attr]
        "🤖 **AIDE-OS Price Tracker — Commands**\n\n"
        "/start — Welcome & overview\n"
        "/track <url> — Track a product\n"
        "/list — List tracked products\n"
        "/setprice <id> <price> — Set alert target\n"
        "/remove <id> — Remove a product\n"
        "/check — Run price check now\n"
        "/help — This message",
        parse_mode="Markdown",
    )


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch any non-command messages and point the user to /help."""
    await update.message.reply_text("🤔 I only understand commands. Try /help for options.")  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------

async def post_init(application: Application) -> None:
    """Set bot commands menu after the application initialises."""
    commands = [
        BotCommand("start", "Welcome & overview"),
        BotCommand("track", "Track a product (URL)"),
        BotCommand("list", "List tracked products"),
        BotCommand("setprice", "Set target price alert"),
        BotCommand("remove", "Remove a tracked product"),
        BotCommand("check", "Run a price check now"),
        BotCommand("help", "Show help"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands registered.")


def build_application() -> Application:
    """Build and configure the telegram Application instance."""
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN not set. "
            "Copy .env.example to .env and fill in your bot token."
        )

    init_db()

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("track", cmd_track))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("remove", cmd_remove))
    app.add_handler(CommandHandler("setprice", cmd_setprice))
    app.add_handler(CommandHandler("check", cmd_check))

    # Fallback for unknown messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))

    return app


def main() -> None:
    """Entry point — start the bot with polling.

    Can be called from another module (``from telegram_bot import main``)
    or executed directly (``python telegram_bot.py``).
    """
    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        level=logging.INFO,
    )
    logger.info("Starting AIDE-OS Price-Drop Bot …")

    app = build_application()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
