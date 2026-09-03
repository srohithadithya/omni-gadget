"""
AIDE-OS — Analytics Service
Wraps DB query helpers for user history, popular products, and market trends.
All methods return empty structures on DB failure.
"""
from app.db import (
    get_user_history as _db_get_user_history,
    get_popular_products as _db_get_popular_products,
    get_market_trends as _db_get_market_trends,
    log_user_device,
    log_emi_audit,
)


class AnalyticsService:
    """Stateless service class — all methods are static and DB-tolerant."""

    @staticmethod
    def log_decision(session_id: str, decision_data: dict) -> bool:
        """
        Log a full-decision or device-longevity result to user_devices.
        Returns True on success, False on failure (never raises).
        """
        try:
            payload = {
                "session_id": session_id,
                "category": decision_data.get("category"),
                "device_brand": decision_data.get("device_brand"),
                "device_model": decision_data.get("device_model"),
                "age_months": decision_data.get("age_months"),
                "battery_health_pct": decision_data.get("battery_health_pct"),
                "storage_health_pct": decision_data.get("storage_health_pct"),
                "physical_condition": decision_data.get("physical_condition"),
                "eol_months": decision_data.get("eol_months"),
                "url_score_pct": decision_data.get("url_score_pct"),
                "estimated_years_left": decision_data.get("estimated_years_left"),
                "decision": decision_data.get("decision"),
            }
            log_user_device(payload)
            return True
        except Exception:
            return False

    @staticmethod
    def log_emi(session_id: str, emi_data: dict) -> bool:
        """
        Log an EMI audit result to emi_audit_log.
        Returns True on success, False on failure (never raises).
        """
        try:
            payload = {
                "gadget_id": emi_data.get("gadget_id"),
                "session_id": session_id,
                "product_msrp": emi_data.get("product_msrp"),
                "no_cost_discount": emi_data.get("no_cost_discount"),
                "bank_processing_fee": emi_data.get("bank_processing_fee"),
                "tenure_months": emi_data.get("tenure_months"),
                "forgone_cash_discount": emi_data.get("forgone_cash_discount"),
                "exchange_bonus": emi_data.get("exchange_bonus"),
                "total_hidden_charges": emi_data.get("total_hidden_charges"),
                "true_effective_outlay": emi_data.get("true_effective_outlay"),
                "recommendation": emi_data.get("recommendation"),
            }
            log_emi_audit(payload)
            return True
        except Exception:
            return False

    @staticmethod
    def get_user_history(session_id: str, limit: int = 10) -> list[dict]:
        """Return the last *limit* decisions for *session_id*. Empty list on error."""
        return _db_get_user_history(session_id, limit=limit)

    @staticmethod
    def get_popular_products() -> list[dict]:
        """Return top 5 most recommended product categories. Empty list on error."""
        return _db_get_popular_products()

    @staticmethod
    def get_market_trends() -> list[dict]:
        """Return average URL scores over time. Empty list on error."""
        return _db_get_market_trends()
