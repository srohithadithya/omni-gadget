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


def get_chipflation_profile(category: str) -> dict | None:
    """Query latest chipflation_index row for a category's component type.
    Returns {index, driver, spot_price, mom_growth, yoy_growth} or None."""
    cfg = get_settings()
    conn = psycopg2.connect(cfg.DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        with conn.cursor() as cur:
            # Map category -> primary component type
            comp_map = {
                'mobile': 'LPDDR5X', 'laptop': 'DDR5_SODIMM',
                'audio': 'LPDDR4X', 'video': 'LPDDR4X',
                'memory': 'NAND_3D_TLC', 'wearable': 'LPDDR4X',
            }
            comp = comp_map.get(category, 'LPDDR4X')
            cur.execute(
                """
                SELECT component_type, spot_price_usd, mom_growth_pct, yoy_growth_pct
                FROM chipflation_index
                WHERE component_type = %s
                ORDER BY recorded_at DESC LIMIT 1
                """,
                (comp,),
            )
            row = cur.fetchone()
            if not row:
                return None
            # Convert yoy growth to approximate chipflation index (1.0 = no inflation)
            ci = 1.0 + (row['yoy_growth_pct'] or 0) / 100.0
            return {
                'index': round(ci, 3),
                'driver': f"{row['component_type']} spot at ${row['spot_price_usd']}/GB, "
                          f"+{row['mom_growth_pct']}% MoM, +{row['yoy_growth_pct']}% YoY",
                'spot_price': row['spot_price_usd'],
                'mom_growth': row['mom_growth_pct'],
                'yoy_growth': row['yoy_growth_pct'],
            }
    except Exception:
        return None
    finally:
        conn.close()


def update_chipflation_index(component_type: str, spot_price_usd: float,
                             mom_growth_pct: float, yoy_growth_pct: float,
                             source: str = 'admin'):
    """Insert a new chipflation_index row (admin endpoint)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chipflation_index
                    (component_type, spot_price_usd, mom_growth_pct, yoy_growth_pct, source)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (component_type, spot_price_usd, mom_growth_pct, yoy_growth_pct, source),
            )
            conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()


def get_latest_chipflation_all():
    """Get latest row per component_type for dashboard display."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (component_type)
                    component_type, spot_price_usd, mom_growth_pct, yoy_growth_pct, source, recorded_at
                FROM chipflation_index
                ORDER BY component_type, recorded_at DESC
                """
            )
            return cur.fetchall()
    except Exception:
        return []
    finally:
        conn.close()


def query_products(category: str, use_cases: list[str], max_budget: float,
                   min_ram: int = None, min_storage: int = None,
                   prefer_refurbished: bool = False):
    """Query gadgets table for matching products, ordered by relevance."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM gadgets
                WHERE category = %s AND is_active = TRUE
                """,
                (category,),
            )
            rows = cur.fetchall()
            return rows  # scoring happens in engine
    except Exception:
        return []
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
