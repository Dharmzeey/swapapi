"""
Pure-Python pricing engine.  No Django dependencies — safe to import anywhere.

Single entry point:
    compute_prices(model_slug, uk_reseller_ngn) -> dict

Returns all 5 price columns derived from the UK reseller price.
"""


def r5k(v: float) -> int:
    """Round to nearest 5 000."""
    return round(v / 5000) * 5000


# ── UK end-user markup tiers ───────────────────────────────────────────────────
def _eu_markup(uk_reseller: int) -> int:
    """
    How much to add on top of uk_reseller to reach the UK end-user price.

    ≤ 200 000           → +50 000 flat
    200 001 – 300 000   → +25 000 flat   (budget range, tight margin)
    300 001 – 700 000   → +50 000 flat
    700 001 – 1 000 000 → +80 000 flat
    > 1 000 000         → 80k + 5 % of excess  (≈ +130k at 2 M)
    """
    if uk_reseller <= 200_000:
        return 30_000
    if uk_reseller <= 300_000:
        return 40_000
    if uk_reseller <= 700_000:
        return 50_000
    if uk_reseller <= 1_000_000:
        return 80_000
    return r5k(80_000 + 0.05 * (uk_reseller - 1_000_000))


# ── Swap-in devaluation (fixed per model) ─────────────────────────────────────
_DEVALUATION: dict = {
    # XR
    "iphone-xr":          60_000,
    'iphone-xs':          80_000,
    'iphone-xs-max':     100_000,
    # 11 series
    "iphone-11":          70_000,
    "iphone-11-pro":     90_000,
    "iphone-11-pro-max": 130_000,
    # 12 series
    "iphone-12-mini":    110_000,
    "iphone-12":         120_000,
    "iphone-12-pro":     170_000,
    "iphone-12-pro-max": 180_000,
    # 13 series
    "iphone-13-mini":    160_000,
    "iphone-13":         170_000,
    "iphone-13-pro":     190_000,
    "iphone-13-pro-max": 200_000,
    # 14 series
    "iphone-14":         170_000,
    "iphone-14-plus":    170_000,
    "iphone-14-pro":     180_000,
    "iphone-14-pro-max": 200_000,
    # 15 series
    "iphone-15":         180_000,
    "iphone-15-plus":    190_000,
    "iphone-15-pro":     210_000,
    "iphone-15-pro-max": 220_000,
    # 16 series
    "iphone-16":         150_000,
    "iphone-16-plus":    150_000,
    "iphone-16-pro":     210_000,
    "iphone-16-pro-max": 220_000,
    # 17 series (update once swap-in market stabilises)
    "iphone-17":         200_000,
    "iphone-17-air":     230_000,
    "iphone-17-pro":     240_000,
    "iphone-17-pro-max": 250_000,
    #
}


def _devaluation(model_slug: str, uk_end: int) -> int:
    """Fixed devaluation for known models; 40 % of uk_end for older/unknown."""
    return _DEVALUATION.get(model_slug, r5k(uk_end * 0.40))


# ── Master function ────────────────────────────────────────────────────────────
def compute_prices(model_slug: str, uk_reseller: int) -> dict:
    """
    Derive all price columns from the UK reseller price.

    Returns:
        uk_reseller  – the input (passed through)
        uk_end       – UK end-user price
        swap_in      – what the shop pays for a used Nigerian phone
        ng_reseller  – Nigerian-phone reseller price
        ng_end       – Nigerian-phone end-user price
    """
    uk_end = r5k(uk_reseller + _eu_markup(uk_reseller))
    swap_in = max(r5k(uk_reseller - _devaluation(model_slug, uk_reseller)), 10_000)

    ng_reseller = r5k(swap_in * 1.10) if swap_in <= 700_000 else swap_in + 55_000
    ng_end = r5k(ng_reseller * 1.05)


    return {
        "uk_reseller": uk_reseller,
        "uk_end":      uk_end,
        "swap_in":     swap_in,
        "ng_reseller": ng_reseller,
        "ng_end":      ng_end,
    }
