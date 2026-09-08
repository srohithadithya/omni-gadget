"""
AIDE-OS API Rate Limiting Dashboard
Usage monitoring and abuse prevention for public API consumers.
"""
import time
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading

logger = logging.getLogger("aide-os.rate_limit")

# In-memory rate limiting store (replace with Redis in production)
_rate_limits: dict[str, dict] = {}
_usage_stats: dict[str, list] = defaultdict(list)
_lock = threading.Lock()

# Default rate limits (requests per minute)
DEFAULT_LIMITS = {
    "anonymous": 30,      # 30 req/min for anonymous users
    "basic": 60,          # 60 req/min for basic tier
    "premium": 120,       # 120 req/min for premium tier
    "admin": 300,         # 300 req/min for admin
}

# Endpoint-specific limits (override defaults)
ENDPOINT_LIMITS = {
    "/api/v1/scrape": 10,           # Scraping is expensive
    "/api/v1/price-compare": 5,     # Multi-platform comparison
    "/api/v1/chipflation/refresh": 2,  # Data refresh
    "/api/v1/full-decision": 20,    # Core endpoint
}


@dataclass
class RateLimitInfo:
    tier: str
    limit: int
    remaining: int
    reset_at: str
    retry_after: Optional[int] = None


@dataclass
class UsageRecord:
    endpoint: str
    client_id: str
    timestamp: str
    response_time_ms: Optional[float] = None
    status_code: int = 200


def _get_client_key(client_id: str, tier: str = "anonymous") -> str:
    """Generate rate limit key for client."""
    return f"{tier}:{client_id}"


def check_rate_limit(client_id: str, endpoint: str, tier: str = "anonymous") -> RateLimitInfo:
    """Check if client has exceeded rate limit."""
    now = time.time()
    minute_key = int(now / 60)  # Current minute window
    
    # Get limit for this endpoint/tier
    limit = ENDPOINT_LIMITS.get(endpoint, DEFAULT_LIMITS.get(tier, 30))
    
    client_key = _get_client_key(client_id, tier)
    
    with _lock:
        if client_key not in _rate_limits:
            _rate_limits[client_key] = {
                "window": minute_key,
                "count": 0,
                "tier": tier,
            }
        
        client_data = _rate_limits[client_key]
        
        # Reset if new minute window
        if client_data["window"] != minute_key:
            client_data["window"] = minute_key
            client_data["count"] = 0
        
        # Check limit
        if client_data["count"] >= limit:
            reset_time = (minute_key + 1) * 60
            retry_after = int(reset_time - now) + 1
            return RateLimitInfo(
                tier=tier,
                limit=limit,
                remaining=0,
                reset_at=datetime.fromtimestamp(reset_time).isoformat(),
                retry_after=retry_after,
            )
        
        # Increment counter
        client_data["count"] += 1
        remaining = limit - client_data["count"]
        reset_time = (minute_key + 1) * 60
        
        return RateLimitInfo(
            tier=tier,
            limit=limit,
            remaining=remaining,
            reset_at=datetime.fromtimestamp(reset_time).isoformat(),
        )


def record_usage(endpoint: str, client_id: str, status_code: int = 200, 
                 response_time_ms: Optional[float] = None, tier: str = "anonymous"):
    """Record API usage for monitoring dashboard."""
    record = UsageRecord(
        endpoint=endpoint,
        client_id=client_id,
        timestamp=datetime.utcnow().isoformat(),
        response_time_ms=response_time_ms,
        status_code=status_code,
    )
    
    with _lock:
        _usage_stats[client_id].append(record)
        
        # Keep only last 1000 records per client
        if len(_usage_stats[client_id]) > 1000:
            _usage_stats[client_id] = _usage_stats[client_id][-1000:]


def get_usage_stats(client_id: Optional[str] = None, 
                    hours: int = 24) -> dict:
    """Get usage statistics for dashboard."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    with _lock:
        if client_id:
            records = [
                r for r in _usage_stats.get(client_id, [])
                if datetime.fromisoformat(r.timestamp.replace('Z', '+00:00')) > cutoff
            ]
        else:
            # Aggregate all clients
            records = []
            for client_records in _usage_stats.values():
                records.extend([
                    r for r in client_records
                    if datetime.fromisoformat(r.timestamp.replace('Z', '+00:00')) > cutoff
                ])
    
    # Calculate stats
    total_requests = len(records)
    unique_clients = len(set(r.client_id for r in records))
    
    # Requests by endpoint
    by_endpoint = defaultdict(int)
    for r in records:
        by_endpoint[r.endpoint] += 1
    
    # Requests by status code
    by_status = defaultdict(int)
    for r in records:
        by_status[str(r.status_code)] += 1
    
    # Average response time
    response_times = [r.response_time_ms for r in records if r.response_time_ms is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Rate limit hits (429 responses)
    rate_limited = sum(1 for r in records if r.status_code == 429)
    
    return {
        "period_hours": hours,
        "total_requests": total_requests,
        "unique_clients": unique_clients,
        "requests_by_endpoint": dict(by_endpoint),
        "requests_by_status": dict(by_status),
        "avg_response_time_ms": round(avg_response_time, 2),
        "rate_limited_requests": rate_limited,
        "rate_limit_hit_rate_pct": round(rate_limited / max(total_requests, 1) * 100, 2),
    }


def get_tier_usage() -> dict:
    """Get usage breakdown by client tier."""
    with _lock:
        tier_counts = {"anonymous": 0, "basic": 0, "premium": 0, "admin": 0}
        
        for client_key, data in _rate_limits.items():
            tier = data.get("tier", "anonymous")
            tier_counts[tier] = tier_counts.get(tier, 0) + data.get("count", 0)
    
    return {
        "tier_usage": tier_counts,
        "total_tracked_clients": len(_rate_limits),
    }


def reset_client_limits(client_id: str, tier: str = "anonymous"):
    """Reset rate limits for a specific client (admin function)."""
    client_key = _get_client_key(client_id, tier)
    
    with _lock:
        if client_key in _rate_limits:
            del _rate_limits[client_key]
    
    logger.info("Reset rate limits for client: %s", client_key)


def get_endpoint_health() -> dict:
    """Get health stats for each endpoint."""
    with _lock:
        all_records = []
        for records in _usage_stats.values():
            all_records.extend(records)
    
    # Group by endpoint
    endpoint_stats = defaultdict(lambda: {"requests": 0, "errors": 0, "avg_time": 0})
    
    for r in all_records:
        stats = endpoint_stats[r.endpoint]
        stats["requests"] += 1
        if r.status_code >= 400:
            stats["errors"] += 1
        if r.response_time_ms:
            stats["avg_time"] = (stats["avg_time"] * (stats["requests"] - 1) + r.response_time_ms) / stats["requests"]
    
    # Convert to dict and add error rates
    result = {}
    for endpoint, stats in endpoint_stats.items():
        result[endpoint] = {
            "total_requests": stats["requests"],
            "error_count": stats["errors"],
            "error_rate_pct": round(stats["errors"] / max(stats["requests"], 1) * 100, 2),
            "avg_response_time_ms": round(stats["avg_time"], 2),
        }
    
    return result
