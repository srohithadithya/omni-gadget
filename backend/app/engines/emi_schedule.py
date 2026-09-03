"""
EMI Schedule Generator — Full Amortization Table
Standard reducing-balance EMI method (Indian banking standard).
"""
from app.config import get_settings

cfg = get_settings()
GST_RATE = cfg.GST_RATE


def generate_emi_schedule(principal: float, annual_rate_pct: float, tenure_months: int) -> list[dict]:
    """
    Generate a month-by-month amortization schedule.

    Parameters
    ----------
    principal : float
        Loan principal (the financed amount, i.e. MSRP minus no-cost discount).
    annual_rate_pct : float
        Annual interest rate in percentage (e.g. 13.0 for 13%).
    tenure_months : int
        Number of months for repayment.

    Returns
    -------
    list[dict] — each dict has:
        month, opening_balance, emi, principal_component,
        interest_component, closing_balance
    """
    monthly_rate = annual_rate_pct / (12 * 100)  # convert annual % to monthly decimal
    schedule = []

    if principal <= 0 or tenure_months <= 0:
        return schedule

    # ── No-Cost EMI (zero interest) ──────────────────────────────────────
    if monthly_rate == 0:
        emi = round(principal / tenure_months, 2)
        balance = principal
        for m in range(1, tenure_months + 1):
            opening = round(balance, 2)
            principal_part = emi if m < tenure_months else round(balance, 2)
            # Last month: pay off whatever remains
            if m == tenure_months:
                principal_part = round(balance, 2)
                emi = principal_part
            closing = round(balance - principal_part, 2)
            if closing < 0.005:
                closing = 0.0
            schedule.append({
                "month": m,
                "opening_balance": opening,
                "emi": round(principal_part, 2),
                "principal_component": round(principal_part, 2),
                "interest_component": 0.0,
                "closing_balance": closing,
            })
            balance = closing
        return schedule

    # ── Standard EMI (reducing balance) ──────────────────────────────────
    factor = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * factor / (factor - 1)
    emi = round(emi, 2)

    balance = principal
    for m in range(1, tenure_months + 1):
        opening = round(balance, 2)
        interest = round(balance * monthly_rate, 2)
        principal_part = round(emi - interest, 2)

        # Last month: absorb rounding residual
        if m == tenure_months:
            principal_part = round(balance, 2)
            emi = round(principal_part + interest, 2)

        closing = round(balance - principal_part, 2)
        if closing < 0.005:
            closing = 0.0

        schedule.append({
            "month": m,
            "opening_balance": opening,
            "emi": round(principal_part + interest, 2),
            "principal_component": round(principal_part, 2),
            "interest_component": interest,
            "closing_balance": closing,
        })
        balance = closing

    return schedule
