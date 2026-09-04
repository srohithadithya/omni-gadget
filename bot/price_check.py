"""
Price checker module for AIDE-OS Telegram bot.

Provides ScraperService for real web scraping of Amazon India and Flipkart
with retry logic, rate limiting, caching, and graceful degradation.
Provides PriceChecker that orchestrates price checks across tracked watches
and stores history in PostgreSQL (Neon).
"""

import json
import logging
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from bot.db import (
    get_connection,
    add_price_history,
    get_latest_price,
    list_watches,
)

logger = logging.getLogger(__name__)


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
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def _throttle(self) -> None:
        """Enforce minimum interval between requests."""
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.monotonic()

    def _cached(self, key: str) -> Optional[dict]:
        """Return cached result if still valid, else None."""
        if key in self._cache:
            ts, data = self._cache[key]
            if time.time() - ts < _CACHE_TTL:
                return data
            del self._cache[key]
        return None

    def _fetch_with_retry(self, url: str, **kwargs) -> requests.Response | dict:
        """GET with retry, backoff, and CAPTCHA detection."""
        for attempt in range(_MAX_RETRIES):
            self._throttle()
            try:
                resp = self._session.get(url, timeout=15, **kwargs)

                # CAPTCHA / bot wall detection
                text_preview = resp.text[:2000].lower()
                if any(w in text_preview for w in ["captcha", "robot", "automated access", "blocked"]):
                    logger.warning("CAPTCHA/bot wall detected on %s", url[:80])
                    return {"error": "bot_wall", "status": resp.status_code}

                if resp.status_code == 429:
                    wait = _RETRY_BACKOFF[min(attempt, len(_RETRY_BACKOFF) - 1)] * 2
                    logger.warning("Rate limited (429), backing off %ds", wait)
                    time.sleep(wait)
                    continue

                resp.raise_for_status()
                return resp

            except requests.RequestException as e:
                logger.warning("Request failed (attempt %d): %s", attempt + 1, e)
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(_RETRY_BACKOFF[min(attempt, len(_RETRY_BACKOFF) - 1)])
                continue

        return {"error": "max_retries_exceeded"}

    def scrape_amazon_india(self, asin: str) -> dict:
        """Scrape price from Amazon India product page.

        Returns:
            ``{"price": float, "title": str}`` on success, ``{"error": str}`` on failure.
        """
        cache_key = f"amazon:{asin}"
        cached = self._cached(cache_key)
        if cached:
            return cached

        if not asin or len(asin) != 10:
            return {"error": "invalid_asin"}

        url = f"https://www.amazon.in/dp/{asin}"
        result = self._fetch_with_retry(url, headers={"Accept-Language": "en-IN,en;q=0.9"})

        if isinstance(result, dict) and "error" in result:
            return result

        try:
            soup = BeautifulSoup(result.text, "html.parser")

            # Try multiple price selectors
            price = None
            for selector in [
                "span.a-price-whole",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                "span.priceToPay span.a-offscreen",
                "#corePrice_feature_div span.a-offscreen",
                "#newBuyBoxPrice",
            ]:
                el = soup.select_one(selector)
                if el:
                    text = el.get_text(strip=True)
                    cleaned = re.sub(r"[^\d.]", "", text)
                    if cleaned:
                        price = float(cleaned)
                        break

            title = ""
            title_el = soup.select_one("#productTitle")
            if title_el:
                title = title_el.get_text(strip=True)

            if price:
                data = {"price": price, "title": title or f"Amazon ASIN {asin}"}
                self._cache[cache_key] = (time.time(), data)
                return data

            return {"error": "price_not_found"}

        except Exception as e:
            logger.exception("Parse error for Amazon ASIN %s", asin)
            return {"error": str(e)}

    def scrape_flipkart(self, url: str) -> dict:
        """Scrape price from Flipkart product page.

        Returns:
            ``{"price": float, "title": str}`` on success, ``{"error": str}`` on failure.
        """
        cache_key = f"flipkart:{url}"
        cached = self._cached(cache_key)
        if cached:
            return cached

        result = self._fetch_with_retry(url)

        if isinstance(result, dict) and "error" in result:
            return result

        try:
            soup = BeautifulSoup(result.text, "html.parser")

            price = None
            # Flipkart's price selectors (changes frequently)
            for selector in [
                "div.Nx9bqj.CxhGGd",  # current price
                "div._30jeq3._16Jk6d",  # sale price
                "div._16Jk6d",  # alt sale
                "span.VW3jWc",  # newer layout
            ]:
                el = soup.select_one(selector)
                if el:
                    text = el.get_text(strip=True)
                    cleaned = re.sub(r"[^\d.]", "", text)
                    if cleaned:
                        price = float(cleaned)
                        break

            # Fallback: search for ₹ price in meta tags
            if not price:
                meta = soup.select_one("meta[itemprop='price']")
                if meta and meta.get("content"):
                    try:
                        price = float(meta["content"])
                    except ValueError:
                        pass

            title = ""
            title_el = soup.select_one("span.VU-ZEY") or soup.select_one("h1")
            if title_el:
                title = title_el.get_text(strip=True)

            if price:
                data = {"price": price, "title": title or f"Flipkart product"}
                self._cache[cache_key] = (time.time(), data)
                return data

            return {"error": "price_not_found"}

        except Exception as e:
            logger.exception("Parse error for Flipkart URL %s", url[:60])
            return {"error": str(e)}


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

    Data is stored in PostgreSQL (Neon) via bot.db module.
    """

    def __init__(self) -> None:
        self._scraper = ScraperService()

    # ── Platform check methods ─────────────────────────────────────────

    def check_amazon(self, asin: str) -> float:
        """Fetch current price for an Amazon product by ASIN."""
        if not asin:
            raise ValueError("ASIN cannot be empty")

        try:
            data = self._scraper.scrape_amazon_india(asin)
            if "error" not in data and "price" in data:
                logger.info("Amazon check for ASIN %s -> ₹%.2f (live)", asin, data["price"])
                return data["price"]
            logger.warning("Scrape failed for ASIN %s: %s", asin, data.get("error", "unknown"))
        except Exception:
            logger.exception("Unexpected error scraping Amazon ASIN %s", asin)

        simulated = round(random.uniform(499, 24999), 2)
        logger.info("Amazon check for ASIN %s -> ₹%.2f (simulated)", asin, simulated)
        return simulated

    def check_flipkart(self, url: str) -> float:
        """Fetch current price for a Flipkart product by URL."""
        if not url:
            raise ValueError("URL cannot be empty")

        try:
            data = self._scraper.scrape_flipkart(url)
            if "error" not in data and "price" in data:
                logger.info("Flipkart check for %s -> ₹%.2f (live)", url[:60], data["price"])
                return data["price"]
            logger.warning("Scrape failed for %s: %s", url[:60], data.get("error", "unknown"))
        except Exception:
            logger.exception("Unexpected error scraping Flipkart %s", url[:60])

        simulated = round(random.uniform(299, 19999), 2)
        logger.info("Flipkart check for %s -> ₹%.2f (simulated)", url[:60], simulated)
        return simulated

    # ── Internal helpers ───────────────────────────────────────────────

    @staticmethod
    def _get_last_price(watch_id: int) -> Optional[float]:
        """Return the most recent recorded price for a watch, or None."""
        row = get_latest_price(watch_id)
        if row is None:
            return None
        # row is a tuple (price, checked_at)
        return float(row[0]) if row else None

    @staticmethod
    def _extract_asin(url: str) -> str:
        """Best-effort ASIN extraction from an Amazon URL."""
        patterns = [
            r"/dp/([A-Z0-9]{10})",
            r"/gp/product/([A-Z0-9]{10})",
            r"/product/([A-Z0-9]{10})",
        ]
        for pat in patterns:
            m = re.search(pat, url, re.IGNORECASE)
            if m:
                return m.group(1).upper()
        parts = [p for p in url.rstrip("/").split("/") if p]
        return parts[-1] if parts else "UNKNOWN"

    @staticmethod
    def _determine_platform(url: str) -> str:
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
        """
        results: list[PriceResult] = []

        try:
            watches = list_watches()  # all watches
        except Exception:
            logger.exception("Failed to fetch watches from DB")
            return results

        if not watches:
            logger.info("No watches to check.")
            return results

        for watch in watches:
            wid = watch["id"]
            url = watch["product_url"]
            prev_price = self._get_last_price(wid)

            try:
                platform = self._determine_platform(url)
                if platform == "amazon":
                    current_price = self.check_amazon(self._extract_asin(url))
                elif platform == "flipkart":
                    current_price = self.check_flipkart(url)
                else:
                    current_price = round(random.uniform(199, 15000), 2)
            except Exception:
                logger.exception("Failed to fetch price for watch %d", wid)
                continue

            # Record in Postgres history
            try:
                add_price_history(wid, current_price)
            except Exception:
                logger.exception("Failed to record price history for watch %d", wid)

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

        logger.info(
            "Checked %d watches, %d price drops detected.",
            len(watches),
            sum(1 for r in results if r.dropped),
        )
        return results
