"""
Database connection utility for AIDE-OS.
Provides a sync PostgreSQL connection via psycopg2 and an async-friendly pool.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import get_settings


def get_connection():
    """Return a new psycopg2 connection (caller must close)."""
    cfg = get_settings()
    return psycopg2.connect(cfg.DATABASE_URL, cursor_factory=RealDictCursor)


def log_user_device(data: dict):
    """Insert a user device telemetry row after /full-decision or /device-longevity."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_devices
                    (session_id, category, device_brand, device_model,
                     age_months, battery_health_pct, storage_health_pct,
                     physical_condition, eol_months, url_score_pct,
                     estimated_years_left, decision)
                VALUES
                    (%(session_id)s, %(category)s, %(device_brand)s, %(device_model)s,
                     %(age_months)s, %(battery_health_pct)s, %(storage_health_pct)s,
                     %(physical_condition)s, %(eol_months)s, %(url_score_pct)s,
                     %(estimated_years_left)s, %(decision)s)
                """,
                data,
            )
            conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()


def log_emi_audit(data: dict):
    """Insert an EMI audit log row after /full-decision or /emi-audit."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO emi_audit_log
                    (gadget_id, session_id, product_msrp, no_cost_discount,
                     bank_processing_fee, tenure_months, forgone_cash_discount,
                     exchange_bonus, total_hidden_charges, true_effective_outlay,
                     recommendation)
                VALUES
                    (%(gadget_id)s, %(session_id)s, %(product_msrp)s, %(no_cost_discount)s,
                     %(bank_processing_fee)s, %(tenure_months)s, %(forgone_cash_discount)s,
                     %(exchange_bonus)s, %(total_hidden_charges)s, %(true_effective_outlay)s,
                     %(recommendation)s)
                """,
                data,
            )
            conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()
