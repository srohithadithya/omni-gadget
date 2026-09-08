"""
AIDE-OS Multi-Platform Price Comparison Engine
Compare prices across 10+ e-commerce platforms simultaneously.
"""
import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("aide-os.price_comparison")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}


@dataclass
class PlatformPrice:
    platform: str
    price: float
    currency: str
    url: str
    availability: str
    seller: Optional[str] = None
    shipping: float = 0.0
    total_cost: float = 0.0
    last_checked: str = ""
    error: Optional[str] = None


@dataclass
class PriceComparison:
    product_query: str
    category: str
    prices: list = field(default_factory=list)
    lowest_price: float = 0.0
    highest_price: float = 0.0
    avg_price: float = 0.0
    savings_vs_highest: float = 0.0
    best_deal_platform: str = ""
    comparison_time: str = ""
    platforms_checked: int = 0


# Platform configurations for scraping
PLATFORMS = {
    'amazon': {
        'name': 'Amazon.in',
        'search_url': 'https://www.amazon.in/s?k={query}',
        'enabled': True,
    },
    'flipkart': {
        'name': 'Flipkart',
        'search_url': 'https://www.flipkart.com/search?q={query}',
        'enabled': True,
    },
    'croma': {
        'name': 'Croma',
        'search_url': 'https://www.croma.com/searchB?q={query}',
        'enabled': True,
    },
    'reliancedigital': {
        'name': 'Reliance Digital',
        'search_url': 'https://www.reliancedigital.in/search?q={query}',
        'enabled': True,
    },
    'vijaysales': {
        'name': 'Vijay Sales',
        'search_url': 'https://www.vijaysales.com/search/{query}',
        'enabled': True,
    },
    'tatacliq': {
        'name': 'Tata CLiQ',
        'search_url': 'https://www.tatacliq.com/search/?searchCategory=all&text={query}',
        'enabled': True,
    },
    'paytm': {
        'name': 'Paytm Mall',
        'search_url': 'https://paytmmall.com/shop/search?q={query}',
        'enabled': True,
    },
    'snapdeal': {
        'name': 'Snapdeal',
        'search_url': 'https://www.snapdeal.com/search?keyword={query}',
        'enabled': True,
    },
    'jiomart': {
        'name': 'JioMart',
        'search_url': 'https://www.jiomart.com/search/{query}',
        'enabled': True,
    },
    'olx': {
        'name': 'OLX (Used)',
        'search_url': 'https://www.olx.in/items/q-{query}',
        'enabled': True,
    },
    'cashify': {
        'name': 'Cashify (Refurbished)',
        'search_url': 'https://www.cashify.in/search?q={query}',
        'enabled': True,
    },
    'amazon_renewed': {
        'name': 'Amazon Renewed',
        'search_url': 'https://www.amazon.in/s?k={query}&i=renewed',
        'enabled': True,
    },
}


async def search_platform(platform_key: str, query: str) -> PlatformPrice:
    """Search a single platform for product prices."""
    platform = PLATFORMS.get(platform_key)
    if not platform or not platform['enabled']:
        return PlatformPrice(
            platform=platform_key,
            price=0.0,
            currency="INR",
            url="",
            availability="unsupported",
            error="Platform not supported"
        )
    
    url = platform['search_url'].format(query=query.replace(' ', '+'))
    
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        price = 0.0
        product_url = url
        availability = "unknown"
        
        # Generic price extraction (varies by platform)
        # Look for common price patterns
        price_patterns = [
            r'₹\s*([\d,]+(?:\.\d{2})?)',
            r'Rs\.?\s*([\d,]+(?:\.\d{2})?)',
            r'INR\s*([\d,]+(?:\.\d{2})?)',
        ]
        
        for pattern in price_patterns:
            matches = soup.find_all(string=re.compile(pattern))
            if matches:
                # Get the first meaningful price (not too small)
                for match in matches:
                    m = re.search(pattern, match)
                    if m:
                        p = float(m.group(1).replace(',', ''))
                        if p > 100:  # Filter out tiny values
                            price = p
                            break
                if price > 0:
                    break
        
        # Try to find product link
        link_el = soup.find('a', href=True)
        if link_el:
            href = link_el.get('href', '')
            if href.startswith('/'):
                # Make absolute URL based on platform
                if 'amazon' in platform_key:
                    product_url = 'https://www.amazon.in' + href
                elif 'flipkart' in platform_key:
                    product_url = 'https://www.flipkart.com' + href
        
        availability = "available" if price > 0 else "not_found"
        
        return PlatformPrice(
            platform=platform['name'],
            price=price,
            currency="INR",
            url=product_url,
            availability=availability,
            last_checked=datetime.utcnow().isoformat(),
            error=None if price > 0 else "Price not found"
        )
    
    except Exception as e:
        logger.warning("Search failed on %s: %s", platform_key, e)
        return PlatformPrice(
            platform=platform['name'],
            price=0.0,
            currency="INR",
            url=url,
            availability="error",
            error=str(e),
            last_checked=datetime.utcnow().isoformat()
        )


async def compare_prices(query: str, category: str = "general") -> PriceComparison:
    """Compare prices across all enabled platforms."""
    import asyncio
    
    # Search all platforms concurrently
    tasks = [
        search_platform(key, query) 
        for key, config in PLATFORMS.items() 
        if config['enabled']
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter valid results
    valid_prices = [
        r for r in results 
        if isinstance(r, PlatformPrice) and r.price > 0
    ]
    
    # Calculate statistics
    if valid_prices:
        prices = [p.price for p in valid_prices]
        lowest = min(prices)
        highest = max(prices)
        avg = sum(prices) / len(prices)
        best_platform = next(p.platform for p in valid_prices if p.price == lowest)
    else:
        lowest = highest = avg = 0.0
        best_platform = ""
    
    comparison = PriceComparison(
        product_query=query,
        category=category,
        prices=valid_prices,
        lowest_price=lowest,
        highest_price=highest,
        avg_price=round(avg, 2),
        savings_vs_highest=round(highest - lowest, 2) if highest > lowest else 0,
        best_deal_platform=best_platform,
        comparison_time=datetime.utcnow().isoformat(),
        platforms_checked=len(valid_prices)
    )
    
    return comparison


def get_supported_platforms() -> list[dict]:
    """List all supported platforms and their status."""
    return [
        {
            "key": key,
            "name": config['name'],
            "enabled": config['enabled'],
            "search_url_template": config['search_url']
        }
        for key, config in PLATFORMS.items()
    ]
