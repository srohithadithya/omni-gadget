"""
AIDE-OS Deal Verification & Crowdsource API
User-submitted deal verification and voting system.
"""
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

logger = logging.getLogger("aide-os.deal_verification")


@dataclass
class DealSubmission:
    deal_id: str = ""
    product_url: str = ""
    platform: str = ""
    product_title: str = ""
    deal_price: float = 0.0
    original_price: float = 0.0
    coupon_code: Optional[str] = None
    submitted_by: str = "anonymous"
    submitted_at: str = ""
    votes_up: int = 0
    votes_down: int = 0
    verification_status: str = "pending"  # pending, verified, expired, fake
    expires_at: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class DealVote:
    deal_id: str
    voter_id: str
    vote: str  # up, down
    reason: Optional[str] = None
    voted_at: str = ""


# In-memory store (replace with DB in production)
_deals_db: dict[str, DealSubmission] = {}
_votes_db: dict[str, list[DealVote]] = {}


def _generate_deal_id(url: str, price: float) -> str:
    """Generate deterministic deal ID from URL + price."""
    raw = f"{url}:{price}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def submit_deal(deal: DealSubmission) -> DealSubmission:
    """Submit a new deal for community verification."""
    deal.deal_id = _generate_deal_id(deal.product_url, deal.deal_price)
    deal.submitted_at = datetime.utcnow().isoformat()
    deal.verification_status = "pending"
    
    # Check if deal already exists
    if deal.deal_id in _deals_db:
        existing = _deals_db[deal.deal_id]
        # Update votes if resubmitted
        existing.votes_up += 1
        return existing
    
    _deals_db[deal.deal_id] = deal
    _votes_db[deal.deal_id] = []
    
    logger.info("New deal submitted: %s at ₹%.0f", deal.product_title, deal.deal_price)
    return deal


def vote_on_deal(deal_id: str, vote: DealVote) -> dict:
    """Vote on a deal (up = real deal, down = fake/expired)."""
    if deal_id not in _deals_db:
        return {"error": "Deal not found", "deal_id": deal_id}
    
    vote.voted_at = datetime.utcnow().isoformat()
    
    # Check if user already voted
    existing_votes = _votes_db.get(deal_id, [])
    for v in existing_votes:
        if v.voter_id == vote.voter_id:
            # Update existing vote
            if v.vote != vote.vote:
                v.vote = vote.vote
                _update_deal_counts(deal_id)
                return {"status": "vote_updated", "deal_id": deal_id}
            return {"status": "already_voted", "deal_id": deal_id}
    
    _votes_db.setdefault(deal_id, []).append(vote)
    _update_deal_counts(deal_id)
    
    return {"status": "vote_recorded", "deal_id": deal_id, "vote": vote.vote}


def _update_deal_counts(deal_id: str):
    """Recalculate vote counts and verification status."""
    deal = _deals_db.get(deal_id)
    if not deal:
        return
    
    votes = _votes_db.get(deal_id, [])
    deal.votes_up = sum(1 for v in votes if v.vote == "up")
    deal.votes_down = sum(1 for v in votes if v.vote == "down")
    
    # Auto-verify/flag based on votes
    total = deal.votes_up + deal.votes_down
    if total >= 3:
        if deal.votes_up > deal.votes_down * 2:
            deal.verification_status = "verified"
        elif deal.votes_down > deal.votes_up * 2:
            deal.verification_status = "fake"
        else:
            deal.verification_status = "contested"


def get_deal(deal_id: str) -> Optional[DealSubmission]:
    """Get a deal by ID."""
    return _deals_db.get(deal_id)


def list_deals(platform: Optional[str] = None, status: Optional[str] = None, 
               min_discount_pct: float = 0) -> list[DealSubmission]:
    """List deals with optional filters."""
    deals = list(_deals_db.values())
    
    if platform:
        deals = [d for d in deals if d.platform.lower() == platform.lower()]
    
    if status:
        deals = [d for d in deals if d.verification_status == status]
    
    if min_discount_pct > 0:
        deals = [d for d in deals 
                 if d.original_price > 0 and 
                 ((d.original_price - d.deal_price) / d.original_price * 100) >= min_discount_pct]
    
    # Sort by votes (best deals first)
    deals.sort(key=lambda d: d.votes_up - d.votes_down, reverse=True)
    
    return deals


def get_deal_stats() -> dict:
    """Get overall deal verification statistics."""
    deals = list(_deals_db.values())
    total = len(deals)
    
    verified = sum(1 for d in deals if d.verification_status == "verified")
    pending = sum(1 for d in deals if d.verification_status == "pending")
    fake = sum(1 for d in deals if d.verification_status == "fake")
    
    platforms = {}
    for d in deals:
        platforms[d.platform] = platforms.get(d.platform, 0) + 1
    
    return {
        "total_deals": total,
        "verified": verified,
        "pending": pending,
        "fake": fake,
        "platforms": platforms,
        "avg_discount_pct": round(
            sum((d.original_price - d.deal_price) / d.original_price * 100 
                for d in deals if d.original_price > 0 and d.deal_price > 0) / max(total, 1), 1
        )
    }
