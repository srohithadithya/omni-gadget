"""
bot_runner.py — Starts the Telegram bot as a daemon thread inside the
FastAPI process.  This avoids a separate deployment / free-tier worker.

Called from main.py lifespan on startup.
"""
import logging
import os
import threading

logger = logging.getLogger("bot_runner")


def _run_bot():
    """Target for the daemon thread — imports and runs the Telegram bot."""
    try:
        # Ensure project root is on sys.path so `bot.*` imports resolve
        import sys
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from bot.telegram_bot import main as bot_main
        logger.info("🤖 Starting Telegram bot in background thread …")
        bot_main()
    except Exception as exc:
        logger.error("Bot thread crashed: %s", exc, exc_info=True)


def start_bot_if_configured() -> threading.Thread | None:
    """
    Start the Telegram bot in a daemon thread if TELEGRAM_BOT_TOKEN is set.
    Returns the thread object, or None if bot is not configured.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.info("TELEGRAM_BOT_TOKEN not set — bot disabled.")
        return None

    t = threading.Thread(target=_run_bot, name="telegram-bot", daemon=True)
    t.start()
    logger.info("🤖 Telegram bot thread started (daemon=True)")
    return t
