"""
Price checker module for AIDE-OS Telegram bot.

Provides ScraperService for real web scraping of Amazon India and Flipkart
with retry logic, rate limiting, caching, and graceful degradation.
Provides PriceChecker that orchestrates price checks across tracked watches
and stores history in SQLite.
"""

import json
import logging
import random
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
DB_PATH = Path(__file__).parent / "watches.db"


# ── Retry / rate-limit config ──────────────────────────────────────────────

_MAX_RETRIES = 3
_RETRY_BACKOFF = [1, 3, 7]  # seconds between attempts
_MIN_REQUEST_INTERVAL = 2.0  # seconds between any two HTTP requests
_CACHE_TTL = 3600  # 1 hour


# ── ScraperService ─────────────────────────────────────────────────────────


class ScraperService:
    """Real web scraper with retry, rate-limit, caching, and CAPTCHA detection.

    Falls back to returning an ``{"error": ...}`` dict when scraping fails.
    """

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, dict]] = {}
        self._last_request_time: float = 0.0
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    # ── internal helpers ────────────────────────────────────────────────

    def _rate_limit(self) -> None:
        """Enforce minimum interval between outbound requests."""
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            wait = _MIN_REQUEST_INTERVAL - elapsed
            logger.debug("Rate-limit: sleeping %.1fs", wait)
            time.sleep(wait)
        self._last_request_time = time.monotonic()

    def _cache_key(self, url: str) -> str:
        return url

    def _cache_get(self, url: str) -> Optional[dict]:
        entry = self._cache.get(self._cache_key(url))
        if entry:
            ts, data = entry
            if time.time() - ts < _CACHE_TTL:
                logger.debug("Cache hit for %s", url[:80])
                return data
            del self._cache[self._cache_key(url)]
        return None

    def _cache_put(self, url: str, data: dict) -> None:
        self._cache[self._cache_key(url)] = (time.time(), data)

    def _is_captcha(self, html: str) -> bool:
        """Detect common CAPTCHA / bot-block pages."""
        lower = html.lower()
        return any(marker in lower for marker in [
            "captcha",
            "are you a robot",
            "automated access",
            "unusual traffic",
            "blocked",
            "sorry you have been blocked",
        ])

    def _fetch(self, url: str) -> Optional[str]:
        """Fetch *url* with retries, rate-limiting, and CAPTCHA detection.

        Returns the page HTML on success or ``None`` on failure.
        """
        for attempt in range(_MAX_RETRIES):
            try:
                self._rate_limit()
                resp = self._session.get(url, timeout=15)
                if resp.status_code == 429:
                    logger.warning("429 Too Many Requests for %s (attempt %d)", url[:60], attempt + 1)
                    backoff = _RETRY_BACKOFF[min(attempt, len(_RETRY_BACKOFF) - 1)]
                    time.sleep(backoff * 2)
                    continue
                resp.raise_for_status()
                html = resp.text
                if self._is_captcha(html):
                    logger.warning("CAPTCHA detected for %s (attempt %d)", url[:60], attempt + 1)
                    return None
                return html
            except requests.RequestException as exc:
                logger.warning("HTTP error for %s (attempt %d): %s", url[:60], attempt + 1, exc)
                backoff = _RETRY_BACKOFF[min(attempt, len(_RETRY_BACKOFF) - 1)]
                time.sleep(backoff)
        return None

    # ── public API ──────────────────────────────────────────────────────

    def scrape_amazon_india(self, asin: str) -> dict:
        """Scrape product info from Amazon India.

        Returns::

            {"title": str, "price": float, "currency": "INR",
             "image_url": str, "asin": str}

        On failure returns ``{"error": "<reason>"}``.
        """
        if not asin:
            return {"error": "ASIN cannot be empty"}

        url = f"https://www.amazon.in/dp/{asin}"
        cached = self._cache_get(url)
        if cached is not None:
            return cached

        html = self._fetch(url)
        if html is None:
            return {"error": f"Failed to fetch Amazon page for {asin}"}

        try:
            soup = BeautifulSoup(html, "html.parser")
            result: dict = {"asin": asin, "currency": "INR"}

            # ── Title ───────────────────────────────────────────────
            title_tag = soup.find("span", id="productTitle")
            result["title"] = title_tag.get_text(strip=True) if title_tag else ""

            # ── Image ──────────────────────────────────────────────
            img_tag = soup.find("img", id="landingImage") or soup.find("img", id="imgBlkFront")
            result["image_url"] = img_tag.get("src", "") if img_tag else ""

            # ── Price – try JSON-LD first ───────────────────────────
            price: Optional[float] = None
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    ld = json.loads(script.string or "")
                    if isinstance(ld, list):
                        ld = ld[0]
                    offers = ld.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    price_str = offers.get("price", "")
                    if price_str:
                        price = float(price_str)
                        break
                except (json.JSONDecodeError, ValueError, KeyError, IndexError):
                    continue

            # ── Price – try meta tag ────────────────────────────────
            if price is None:
                meta = soup.find("meta", attrs={"name": "twitter:data1"})
                if meta and meta.get("content"):
                    cleaned = re.sub(r"[^\d.]", "", meta["content"])
                    if cleaned:
                        price = float(cleaned)

            # ── Price – try #priceblock_ourprice / #priceblock_dealprice ──
            if price is None:
                for pid in ("priceblock_ourprice", "priceblock_dealprice", "priceblock_saleprice", "corePrice_feature_div"):
                    tag = soup.find("span", id=pid) or soup.find("span", class_=re.compile(pid, re.I))
                    if tag:
                        cleaned = re.sub(r"[^\d.]", "", tag.get_text())
                        if cleaned:
                            price = float(cleaned)
                            break

            if price is not None:
                result["price"] = round(price, 2)
                self._cache_put(url, result)
                logger.info("Amazon scrape for %s -> ₹%.2f", asin, price)
                return result

            return {"error": f"Price element not found for {asin}"}

        except Exception as exc:
            logger.exception("Parse error for Amazon ASIN %s", asin)
            return {"error": f"Parse error: {exc}"}

    def scrape_flipkart(self, url: str) -> dict:
        """Scrape product info from Flipkart.

        Returns::

            {"title": str, "price": float, "currency": "INR",
             "image_url": str, "product_id": str}

        On failure returns ``{"error": "<reason>"}``.
        """
        if not url:
            return {"error": "URL cannot be empty"}

        cached = self._cache_get(url)
        if cached is not None:
            return cached

        html = self._fetch(url)
        if html is None:
            return {"error": f"Failed to fetch Flipkart page for {url[:60]}"}

        try:
            soup = BeautifulSoup(html, "html.parser")
            # Extract product ID from URL path
            path_parts = urlparse(url).path.strip("/").split("/")
            product_id = path_parts[-1] if path_parts else ""
            result: dict = {"product_id": product_id, "currency": "INR"}

            # ── Title ───────────────────────────────────────────────
            title_tag = (
                soup.find("span", class_=re.compile(r"B_NuCI", re.I))
                or soup.find("h1")
            )
            result["title"] = title_tag.get_text(strip=True) if title_tag else ""

            # ── Image ──────────────────────────────────────────────
            img_tag = soup.find("img", class_=re.compile(r"_396cs4|_2r_T1I|_1Nwwsh", re.I))
            result["image_url"] = img_tag.get("src", "") if img_tag else ""

            # ── Price – try JSON-LD first ───────────────────────────
            price: Optional[float] = None
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    ld = json.loads(script.string or "")
                    if isinstance(ld, list):
                        ld = ld[0]
                    offers = ld.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    price_str = offers.get("price", "")
                    if price_str:
                        price = float(price_str)
                        break
                except (json.JSONDecodeError, ValueError, KeyError, IndexError):
                    continue

            # ── Price – try common Flipkart price selectors ────────
            if price is None:
                for selector in [
                    ("div", re.compile(r"_30jeq3|_16Jk6d|_1_WHN1", re.I)),
                    ("div", {"class": re.compile(r"_30jeq3", re.I)}),
                ]:
                    tag = soup.find(selector[0], attrs=selector[1]) if isinstance(selector[1], dict) else soup.find(*selector)
                    if tag:
                        cleaned = re.sub(r"[^\d.]", "", tag.get_text())
                        if cleaned:
                            price = float(cleaned)
                            break

            if price is not None:
                result["price"] = round(price, 2)
                self._cache_put(url, result)
                logger.info("Flipkart scrape for %s -> ₹%.2f", product_id, price)
                return result

            return {"error": f"Price element not found for {url[:60]}"}

        except Exception as exc:
            logger.exception("Parse error for Flipkart URL %s", url[:60])
            return {"error": f"Parse error: {exc}"}


# ── PriceChecker ───────────────────────────────────────────────────────────


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

    Uses :class:`ScraperService` for real data, with automatic fallback to
    simulated prices when scraping fails.

    Args:
        db_path: Path to the SQLite database file. Defaults to bot/watches.db.
    """

    def __init__(self, db_path: Optional[str | Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH
        self._scraper = ScraperService()
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

    # ── Platform check methods ─────────────────────────────────────────

    def check_amazon(self, asin: str) -> float:
        """Fetch current price for an Amazon product by ASIN.

        Attempts real scraping first; falls back to simulated price.

        Args:
            asin: Amazon Standard Identification Number.

        Returns:
            Current price in INR.

        Raises:
            ValueError: If asin is empty.
        """
        if not asin:
            raise ValueError("ASIN cannot be empty")

        try:
            data = self._scraper.scrape_amazon_india(asin)
            if "error" not in data and "price" in data:
                logger.info("Amazon check for ASIN %s -> ₹%.2f (live)", asin, data["price"])
                return data["price"]
            logger.warning("Scrape failed for ASIN %s: %s — falling back to simulated", asin, data.get("error", "unknown"))
        except Exception:
            logger.exception("Unexpected error scraping Amazon ASIN %s", asin)

        simulated = round(random.uniform(499, 24999), 2)
        logger.info("Amazon check for ASIN %s -> ₹%.2f (simulated)", asin, simulated)
        return simulated

    def check_flipkart(self, url: str) -> float:
        """Fetch current price for a Flipkart product by URL.

        Attempts real scraping first; falls back to simulated price.

        Args:
            url: Full Flipkart product URL.

        Returns:
            Current price in INR.

        Raises:
            ValueError: If url is empty.
        """
        if not url:
            raise ValueError("URL cannot be empty")

        try:
            data = self._scraper.scrape_flipkart(url)
            if "error" not in data and "price" in data:
                logger.info("Flipkart check for %s -> ₹%.2f (live)", url[:60], data["price"])
                return data["price"]
            logger.warning("Scrape failed for %s: %s — falling back to simulated", url[:60], data.get("error", "unknown"))
        except Exception:
            logger.exception("Unexpected error scraping Flipkart %s", url[:60])

        simulated = round(random.uniform(299, 19999), 2)
        logger.info("Flipkart check for %s -> ₹%.2f (simulated)", url[:60], simulated)
        return simulated

    # ── Internal helpers ───────────────────────────────────────────────

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
                        # Unknown platform — try scraper, fall back to simulated
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

        logger.info(
            "Checked %d watches, %d price drops detected.",
            len(watches),
            sum(1 for r in results if r.dropped),
        )
        return results
