"""
Price checker module for AIDE-OS Telegram bot.

Provides the PriceChecker class that handles price fetching and comparison
for tracked products on Amazon and Flipkart. Currently uses simulated prices
for development; real scraping can be plugged in later.
"""

import logging
import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "watches.db"


@dataclass
class PriceResult:
    """Result of a single price check."""

    watch_id: int
    user_id: int
    product_url: str
    product_name: str
    current_price: float
    previous_price: float
    target_price: float
    dropped: bool
    meets_target: bool


class PriceChecker:
    """Checks prices for tracked products and detects drops.

    Args:
        db_path: Path to the SQLite database file. Defaults to bot/watches.db.
    """

    def __init__(self, db_path: Optional[str | Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found at {self.db_path}. "
                "Run the bot first to create it."
            )

    def _connect(self) -> sqlite3.Connection:
        """Open a short-lived SQLite connection (autocommit for reads)."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Platform stubs
    # ------------------------------------------------------------------

    def check_amazon(self, asin: str) -> float:
        """Fetch current price for an Amazon product by ASIN.

        Currently returns a simulated price between ₹499 and ₹24,999.

        Args:
            asin: Amazon Standard Identification Number.

        Returns:
            Current price in INR.

        Raises:
            ValueError: If asin is empty.
        """
        if not asin:
            raise ValueError("ASIN cannot be empty")
        simulated = round(random.uniform(499, 24999), 2)
        logger.info("Amazon check for ASIN %s -> ₹%.2f (simulated)", asin, simulated)
        return simulated

    def check_flipkart(self, url: str) -> float:
        """Fetch current price for a Flipkart product by URL.

        Currently returns a simulated price between ₹299 and ₹19,999.

        Args:
            url: Full Flipkart product URL.

        Returns:
            Current price in INR.

        Raises:
            ValueError: If url is empty.
        """
        if not url:
            raise ValueError("URL cannot be empty")
        simulated = round(random.uniform(299, 19999), 2)
        logger.info("Flipkart check for %s -> ₹%.2f (simulated)", url[:60], simulated)
        return simulated

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    def _get_last_price(self, conn: sqlite3.Connection, watch_id: int) -> Optional[float]:
        """Return the most recent recorded price for a watch, or None."""
        row = conn.execute(
            "SELECT price FROM price_history WHERE watch_id = ? ORDER BY checked_at DESC LIMIT 1",
            (watch_id,),
        ).fetchone()
        return float(row["price"]) if row else None

    def _extract_asin(self, url: str) -> str:
        """Best-effort ASIN extraction from an Amazon URL.

        Tries common patterns:
          - /dp/<ASIN>
          - /gp/product/<ASIN>
          - /product/<ASIN>
        Falls back to the last URL segment.
        """
        import re

        patterns = [
            r"/dp/([A-Z0-9]{10})",
            r"/gp/product/([A-Z0-9]{10})",
            r"/product/([A-Z0-9]{10})",
        ]
        for pat in patterns:
            m = re.search(pat, url, re.IGNORECASE)
            if m:
                return m.group(1).upper()
        # fallback: last non-empty segment
        parts = [p for p in url.rstrip("/").split("/") if p]
        return parts[-1] if parts else "UNKNOWN"

    def _determine_platform(self, url: str) -> str:
        """Return 'amazon' or 'flipkart' based on the URL hostname."""
        lower = url.lower()
        if "amazon" in lower:
            return "amazon"
        if "flipkart" in lower:
            return "flipkart"
        return "unknown"

    def check_all_watches(self) -> list[PriceResult]:
        """Iterate every tracked watch, fetch the current price, log history,
        and return results including whether the price dropped.

        Returns:
            List of PriceResult objects — one per tracked product.
        """
        results: list[PriceResult] = []

        conn = self._connect()
        try:
            watches = conn.execute(
                "SELECT id, user_id, product_url, product_name, target_price FROM watches"
            ).fetchall()

            if not watches:
                logger.info("No watches to check.")
                return results

            now = datetime.now(timezone.utc).isoformat()

            for watch in watches:
                wid = watch["id"]
                url = watch["product_url"]
                prev_price = self._get_last_price(conn, wid)

                try:
                    platform = self._determine_platform(url)
                    if platform == "amazon":
                        current_price = self.check_amazon(self._extract_asin(url))
                    elif platform == "flipkart":
                        current_price = self.check_flipkart(url)
                    else:
                        # Unknown platform — simulate a generic price
                        current_price = round(random.uniform(199, 15000), 2)
                except Exception:
                    logger.exception("Failed to fetch price for watch %d", wid)
                    continue

                # Record in history
                conn.execute(
                    "INSERT INTO price_history (watch_id, price, checked_at) VALUES (?, ?, ?)",
                    (wid, current_price, now),
                )
                conn.commit()

                dropped = prev_price is not None and current_price < prev_price
                meets_target = (
                    watch["target_price"] > 0 and current_price <= watch["target_price"]
                )

                results.append(
                    PriceResult(
                        watch_id=wid,
                        user_id=watch["user_id"],
                        product_url=url,
                        product_name=watch["product_name"],
                        current_price=current_price,
                        previous_price=prev_price or current_price,
                        target_price=watch["target_price"],
                        dropped=dropped,
                        meets_target=meets_target,
                    )
                )

        finally:
            conn.close()

        logger.info("Checked %d watches, %d price drops detected.",
                     len(watches), sum(1 for r in results if r.dropped))
        return results
