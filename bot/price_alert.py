"""
Price alert module for AIDE-OS Telegram bot.

Provides PriceAlertManager for detecting target-price hits and sending
Telegram notifications when prices drop.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PriceAlertManager:
    """Manages price-drop alerts and Telegram notifications.

    Can be used standalone (returns messages for callers to send) or with a
    ``python-telegram-bot`` ``Application`` instance for direct notification.
    """

    def __init__(self, telegram_app=None) -> None:
        """
        Args:
            telegram_app: Optional ``python-telegram-bot`` Application or
                Bot instance. When provided, ``send_notification`` will push
                messages directly.
        """
        self._app = telegram_app

    # ── Core logic ─────────────────────────────────────────────────────

    def check_and_alert(
        self,
        user_id: int,
        product_id: str,
        current_price: float,
        target_price: float,
        product_name: str = "",
        product_url: str = "",
        old_price: Optional[float] = None,
    ) -> Optional[str]:
        """Return an alert message when *current_price* ≤ *target_price*, else None.

        Args:
            user_id: Telegram chat / user ID.
            product_id: Platform product identifier.
            current_price: Latest observed price.
            target_price: User's desired maximum price.
            product_name: Human-readable product name (for the message).
            product_url: Product URL (for the message).
            old_price: Previous price for the drop message.

        Returns:
            Formatted alert string, or ``None`` if no alert is warranted.
        """
        if target_price <= 0:
            return None

        if current_price > target_price:
            return None

        # Build message
        if old_price is not None and old_price > current_price:
            message = self.format_price_drop_message(
                product_name or product_id,
                old_price,
                current_price,
                product_url,
            )
        else:
            message = (
                f"🎯 Target price reached!\n\n"
                f"📦 *{_escape_md(product_name or product_id)}*\n"
                f"💰 Current price: ₹{current_price:,.2f}\n"
                f"🎯 Your target: ₹{target_price:,.2f}\n"
            )
            if product_url:
                message += f"\n🔗 {product_url}"

        logger.info(
            "Alert triggered for user %d, product %s: ₹%.2f ≤ ₹%.2f",
            user_id,
            product_id,
            current_price,
            target_price,
        )
        return message

    # ── Message formatting ─────────────────────────────────────────────

    @staticmethod
    def format_price_drop_message(
        product_name: str,
        old_price: float,
        new_price: float,
        url: str = "",
    ) -> str:
        """Format a human-readable price drop notification string.

        Args:
            product_name: Product title.
            old_price: Previous price.
            new_price: New (lower) price.
            url: Product URL.

        Returns:
            Formatted string suitable for Telegram (Markdown).
        """
        drop_pct = ((old_price - new_price) / old_price) * 100 if old_price > 0 else 0

        lines = [
            "📉 Price Drop Alert!\n",
            f"📦 *{_escape_md(product_name)}*",
            f"💲 Was: ₹{old_price:,.2f}",
            f"💰 Now: ₹{new_price:,.2f}",
            f"🔥 Save: ₹{old_price - new_price:,.2f} ({drop_pct:.1f}% off)",
        ]
        if url:
            lines.append(f"\n🔗 {url}")
        return "\n".join(lines)

    # ── Telegram sending ───────────────────────────────────────────────

    async def send_notification(self, chat_id: int, message: str) -> bool:
        """Send a message to a Telegram chat via the configured bot.

        Args:
            chat_id: Telegram chat / user ID.
            message: Markdown-formatted message.

        Returns:
            True if sent successfully, False otherwise.
        """
        if self._app is None:
            logger.warning("No Telegram app configured — cannot send notification")
            return False

        try:
            bot = self._app.bot
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
            )
            logger.info("Notification sent to chat %d", chat_id)
            return True
        except Exception:
            logger.exception("Failed to send Telegram notification to %d", chat_id)
            return False


def _escape_md(text: str) -> str:
    """Escape Markdown special characters for Telegram MarkdownV2 where
    simple Markdown v1 is not supported."""
    # For Markdown v1 (used here), only escape _ * ` [ with backslash
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text
