"""
Module 7: True-Cost EMI & Hidden Charges Extractor
Exposes processing fees, GST on interest, and forgone cash discounts.
"""
from dataclasses import dataclass


GST_RATE = 0.18  # 18% India GST


@dataclass
class EMIInput:
    product_msrp: float
    no_cost_discount: float       # Interest subsidy provided by seller
    bank_processing_fee: float    # Typically ₹199–₹299
    tenure_months: int
    forgone_cash_discount: float  # Instant UPI/Debit discount lost by choosing EMI
    exchange_bonus: float = 0.0   # Trade-in value


@dataclass
class EMIResult:
    advertised_price: float
    breakdown: dict
    total_hidden_charges: float
    true_effective_outlay: float
    hidden_charge_pct: float
    monthly_emi: float
    recommendation: str
    advice: str


def calculate_true_emi_cost(inp: EMIInput) -> EMIResult:
    # GST on processing fee
    gst_on_processing = inp.bank_processing_fee * GST_RATE

    # 18% GST on the interest component — never refunded by seller
    gst_on_interest = inp.no_cost_discount * GST_RATE

    total_hidden = (
        inp.bank_processing_fee
        + gst_on_processing
        + gst_on_interest
        + inp.forgone_cash_discount
    )

    true_cost = inp.product_msrp + total_hidden - inp.exchange_bonus
    hidden_pct = round((total_hidden / inp.product_msrp) * 100, 2)

    # Effective monthly EMI on true cost
    monthly_emi = round(true_cost / inp.tenure_months, 2)

    if total_hidden > 2000:
        recommendation = "PAY_UPFRONT_CASH"
        advice = (
            f"Hidden charges total ₹{total_hidden:,.2f} ({hidden_pct}% of price). "
            "Pay upfront via UPI/Debit card to save this amount outright."
        )
    elif total_hidden > 800:
        recommendation = "RECONSIDER_EMI_TENURE"
        advice = (
            f"Hidden charges of ₹{total_hidden:,.2f} are significant. "
            "Consider a shorter EMI tenure (3–6 months) to reduce interest GST exposure."
        )
    else:
        recommendation = "EMI_ACCEPTABLE"
        advice = (
            f"Hidden charges are modest at ₹{total_hidden:,.2f}. "
            "No-Cost EMI is a reasonable option here."
        )

    return EMIResult(
        advertised_price=inp.product_msrp,
        breakdown={
            "bank_processing_fee": round(inp.bank_processing_fee, 2),
            "gst_on_processing_fee_18pct": round(gst_on_processing, 2),
            "unrefundable_gst_on_interest_18pct": round(gst_on_interest, 2),
            "forgone_upfront_cash_discount": round(inp.forgone_cash_discount, 2),
            "exchange_bonus_deducted": round(inp.exchange_bonus, 2),
        },
        total_hidden_charges=round(total_hidden, 2),
        true_effective_outlay=round(true_cost, 2),
        hidden_charge_pct=hidden_pct,
        monthly_emi=monthly_emi,
        recommendation=recommendation,
        advice=advice,
    )
