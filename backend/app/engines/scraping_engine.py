"""AIDE-OS Price Scraper Engine
Real-time product price scraping from Amazon.in and Flipkart.com
"""
import re
import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("aide-os.scraper")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}


@dataclass
class ScrapeResult:
    product_id: str
    platform: str  # amazon, flipkart
    title: str
    price: float
    currency: str
    image_url: Optional[str] = None
    availability: str = "unknown"
    rating: Optional[float] = None
    review_count: Optional[int] = None
    url: str = ""
    scraped_at: str = ""
    error: Optional[str] = None


def extract_amazon_asin(url: str) -> Optional[str]:
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'/ASIN/([A-Z0-9]{10})',
        r'amazon\\.in/[^/]+/([A-Z0-9]{10})',
    ]
    for pat in patterns:
        m = re.search(pat, url, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def extract_flipkart_product_id(url: str) -> Optional[str]:
    patterns = [
        r'/product/p/([A-Z0-9]+)',
        r'/p/([A-Z0-9]+)',
        r'[?&]pid=([A-Z0-9]+)',
    ]
    for pat in patterns:
        m = re.search(pat, url, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


async def scrape_amazon(url: str) -> ScrapeResult:
    asin = extract_amazon_asin(url)
    if not asin:
        return ScrapeResult(
            product_id="", platform="amazon", title="", price=0.0,
            currency="INR", url=url, scraped_at=datetime.utcnow().isoformat(),
            error="Could not extract ASIN from URL"
        )

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
    except Exception as e:
        logger.error("Amazon request failed for %s: %s", url, e)
        return ScrapeResult(
            product_id=asin, platform="amazon", title="", price=0.0,
            currency="INR", url=url, scraped_at=datetime.utcnow().isoformat(),
            error=f"Request failed: {str(e)}"
        )

    soup = BeautifulSoup(resp.text, 'html.parser')

    title = ""
    title_el = soup.find('span', {'id': 'productTitle'})
    if title_el:
        title = title_el.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True).split(' - ')[0].split(' | ')[0]

    price = 0.0
    price_el = soup.find('span', {'class': 'a-price-whole'})
    if price_el:
        price_text = price_el.get_text(strip=True).replace(',', '').replace('.', '')
        price = float(price_text) if price_text.isdigit() else 0.0
    else:
        price_el = soup.find('span', class_=re.compile(r'price'))
        if price_el:
            m = re.search(r'[\\d,]+', price_el.get_text())
            if m:
                price = float(m.group().replace(',', ''))

    image_url = None
    img_el = soup.find('img', {'id': 'landingImage'}) or soup.find('img', {'id': 'imgBlkFront'})
    if img_el:
        image_url = img_el.get('src') or img_el.get('data-old-hires')

    rating = None
    rating_el = soup.find('span', {'class': 'a-icon-alt'})
    if rating_el:
        m = re.search(r'([\\d.]+) out of', rating_el.get_text())
        if m:
            rating = float(m.group(1))

    review_count = None
    review_el = soup.find('span', {'id': 'acrCustomerReviewText'})
    if review_el:
        m = re.search(r'([\\d,]+)', review_el.get_text())
        if m:
            review_count = int(m.group(1).replace(',', ''))

    return ScrapeResult(
        product_id=asin,
        platform="amazon",
        title=title,
        price=price,
        currency="INR",
        image_url=image_url,
        availability="unknown",
        rating=rating,
        review_count=review_count,
        url=url,
        scraped_at=datetime.utcnow().isoformat(),
        error=None if price > 0 and title else "Missing critical data"
    )


async def scrape_flipkart(url: str) -> ScrapeResult:
    pid = extract_flipkart_product_id(url)
    if not pid:
        return ScrapeResult(
            product_id="", platform="flipkart", title="", price=0.0,
            currency="INR", url=url, scraped_at=datetime.utcnow().isoformat(),
            error="Could not extract product ID from URL"
        )

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
    except Exception as e:
        logger.error("Flipkart request failed for %s: %s", url, e)
        return ScrapeResult(
            product_id=pid, platform="flipkart", title="", price=0.0,
            currency="INR", url=url, scraped_at=datetime.utcnow().isoformat(),
            error=f"Request failed: {str(e)}"
        )

    soup = BeautifulSoup(resp.text, 'html.parser')

    title = ""
    title_el = soup.find('span', {'class': 'B_NuCI'}) or soup.find('h1', {'class': '_6EBuvT'})
    if title_el:
        title = title_el.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True).split(' - ')[0].split(' | ')[0]

    price = 0.0
    price_el = soup.find('div', {'class': '_30jeq3._16Jk6d'})
    if price_el:
        price_text = price_el.get_text(strip=True).replace(',', '')
        price = float(price_text) if price_text.replace('.', '', 1).isdigit() else 0.0
    else:
        price_el = soup.find('div', class_=re.compile(r'_30jeq3'))
        if price_el:
            price_text = price_el.get_text(strip=True).replace(',', '')
            price = float(price_text) if price_text.replace('.', '', 1).isdigit() else 0.0

    image_url = None
    img_el = soup.find('img', {'class': '_396cs4 _3exPp9'}) or soup.find('img', {'class': '_2r_T1I _396QI4'})
    if img_el:
        image_url = img_el.get('src')

    rating = None
    rating_el = soup.find('div', {'class': '_3LWZlK'}) or soup.find('div', {'class': '_2d4LTz'})
    if rating_el:
        m = re.search(r'([\\d.]+)', rating_el.get_text())
        if m:
            rating = float(m.group(1))

    review_count = None
    review_el = soup.find('span', {'class': '_2_R_DZ'}) or soup.find('span', {'class': '_13vCMQ'})
    if review_el:
        m = re.search(r'([\\d,]+)', review_el.get_text())
        if m:
            review_count = int(m.group(1).replace(',', ''))

    return ScrapeResult(
        product_id=pid,
        platform="flipkart",
        title=title,
        price=price,
        currency="INR",
        image_url=image_url,
        availability="unknown",
        rating=rating,
        review_count=review_count,
        url=url,
        scraped_at=datetime.utcnow().isoformat(),
        error=None if price > 0 and title else "Missing critical data"
    )


async def scrape_product(url: str) -> ScrapeResult:
    url_lower = url.lower()
    if 'amazon.in' in url_lower or 'amazon.com' in url_lower:
        return await scrape_amazon(url)
    elif 'flipkart.com' in url_lower:
        return await scrape_flipkart(url)
    else:
        return ScrapeResult(
            product_id="", platform="unknown", title="", price=0.0,
            currency="INR", url=url, scraped_at=datetime.utcnow().isoformat(),
            error="Unsupported platform. Use Amazon.in or Flipkart.com URLs."
        )