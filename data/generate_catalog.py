"""
Generates data/iphone_catalog.csv with all price columns.

Run with plain Python (no Django):
    python data/generate_catalog.py

Pricing logic lives in core/pricing.py — edit devaluation amounts or markup
tiers there.  This script only holds the catalog rows (model + UK reseller price).
"""

import csv
import sys
from pathlib import Path

# Allow importing core.pricing without a full Django setup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.pricing import compute_prices  # noqa: E402

OUT = Path(__file__).parent


# ─────────────────────────────────────────────────────────────────────────────
# CATALOG — one row per variant
#
# Columns: series_name, series_order, model_name, model_slug,
#          variant_type, model_order, capacity,
#          uk_reseller_price_ngn   ← ONLY THIS FIELD NEEDS UPDATING
# ─────────────────────────────────────────────────────────────────────────────
ROWS = [
    # ── iPhone 6 ──────────────────────────────────────────────────────────────
    ("6",  0, "iPhone 6",       "iphone-6",       "standard", 0, "16GB",   45000),
    ("6",  0, "iPhone 6",       "iphone-6",       "standard", 0, "32GB",   50000),
    ("6",  0, "iPhone 6",       "iphone-6",       "standard", 0, "64GB",   55000),
    ("6",  0, "iPhone 6",       "iphone-6",       "standard", 0, "128GB",  65000),
    ("6",  0, "iPhone 6 Plus",  "iphone-6-plus",  "plus",     1, "16GB",   50000),
    ("6",  0, "iPhone 6 Plus",  "iphone-6-plus",  "plus",     1, "64GB",   65000),
    ("6",  0, "iPhone 6 Plus",  "iphone-6-plus",  "plus",     1, "128GB",  75000),
    ("6",  0, "iPhone 6s",      "iphone-6s",      "s",        2, "16GB",   55000),
    ("6",  0, "iPhone 6s",      "iphone-6s",      "s",        2, "32GB",   60000),
    ("6",  0, "iPhone 6s",      "iphone-6s",      "s",        2, "64GB",   70000),
    ("6",  0, "iPhone 6s",      "iphone-6s",      "s",        2, "128GB",  80000),
    ("6",  0, "iPhone 6s Plus", "iphone-6s-plus", "s-plus",   3, "16GB",   60000),
    ("6",  0, "iPhone 6s Plus", "iphone-6s-plus", "s-plus",   3, "32GB",   70000),
    ("6",  0, "iPhone 6s Plus", "iphone-6s-plus", "s-plus",   3, "64GB",   80000),
    ("6",  0, "iPhone 6s Plus", "iphone-6s-plus", "s-plus",   3, "128GB",  95000),
    # ── iPhone 7 ──────────────────────────────────────────────────────────────
    ("7",  1, "iPhone 7",       "iphone-7",       "standard", 0, "32GB",   85000),
    ("7",  1, "iPhone 7",       "iphone-7",       "standard", 0, "128GB", 105000),
    ("7",  1, "iPhone 7",       "iphone-7",       "standard", 0, "256GB", 120000),
    ("7",  1, "iPhone 7 Plus",  "iphone-7-plus",  "plus",     1, "32GB",  100000),
    ("7",  1, "iPhone 7 Plus",  "iphone-7-plus",  "plus",     1, "128GB", 120000),
    ("7",  1, "iPhone 7 Plus",  "iphone-7-plus",  "plus",     1, "256GB", 140000),
    # ── iPhone 8 ──────────────────────────────────────────────────────────────
    ("8",  2, "iPhone 8",       "iphone-8",       "standard", 0, "64GB",  130000),
    ("8",  2, "iPhone 8",       "iphone-8",       "standard", 0, "128GB", 150000),
    ("8",  2, "iPhone 8",       "iphone-8",       "standard", 0, "256GB", 175000),
    ("8",  2, "iPhone 8 Plus",  "iphone-8-plus",  "plus",     1, "64GB",  155000),
    ("8",  2, "iPhone 8 Plus",  "iphone-8-plus",  "plus",     1, "128GB", 180000),
    ("8",  2, "iPhone 8 Plus",  "iphone-8-plus",  "plus",     1, "256GB", 205000),
    # ── iPhone X series ───────────────────────────────────────────────────────
    ("X",  3, "iPhone X",       "iphone-x",       "standard", 0, "64GB",  200000),
    ("X",  3, "iPhone X",       "iphone-x",       "standard", 0, "256GB", 230000),
    ("X",  3, "iPhone XS",      "iphone-xs",      "s",        1, "64GB",  220000),
    ("X",  3, "iPhone XS",      "iphone-xs",      "s",        1, "256GB", 260000),
    ("X",  3, "iPhone XS",      "iphone-xs",      "s",        1, "512GB", 305000),
    ("X",  3, "iPhone XS Max",  "iphone-xs-max",  "max",      2, "64GB",  240000),
    ("X",  3, "iPhone XS Max",  "iphone-xs-max",  "max",      2, "256GB", 285000),
    ("X",  3, "iPhone XS Max",  "iphone-xs-max",  "max",      2, "512GB", 325000),
    ("X",  3, "iPhone XR",      "iphone-xr",      "xr",       3, "64GB",  185000),
    ("X",  3, "iPhone XR",      "iphone-xr",      "xr",       3, "128GB", 210000),
    ("X",  3, "iPhone XR",      "iphone-xr",      "xr",       3, "256GB", 235000),
    # ── iPhone 11 ─────────────────────────────────────────────────────────────
    ("11", 4, "iPhone 11",          "iphone-11",          "standard", 0, "64GB",  215000),
    ("11", 4, "iPhone 11",          "iphone-11",          "standard", 0, "128GB", 250000),
    ("11", 4, "iPhone 11",          "iphone-11",          "standard", 0, "256GB", 285000),
    ("11", 4, "iPhone 11 Pro",      "iphone-11-pro",      "pro",      1, "64GB",  260000),
    ("11", 4, "iPhone 11 Pro",      "iphone-11-pro",      "pro",      1, "256GB", 310000),
    ("11", 4, "iPhone 11 Pro",      "iphone-11-pro",      "pro",      1, "512GB", 360000),
    ("11", 4, "iPhone 11 Pro Max",  "iphone-11-pro-max",  "max",      2, "64GB",  285000),
    ("11", 4, "iPhone 11 Pro Max",  "iphone-11-pro-max",  "max",      2, "256GB", 335000),
    ("11", 4, "iPhone 11 Pro Max",  "iphone-11-pro-max",  "max",      2, "512GB", 385000),
    # ── iPhone 12 ─────────────────────────────────────────────────────────────
    ("12", 5, "iPhone 12 mini",     "iphone-12-mini",     "mini",     0, "64GB",  260000),
    ("12", 5, "iPhone 12 mini",     "iphone-12-mini",     "mini",     0, "128GB", 295000),
    ("12", 5, "iPhone 12 mini",     "iphone-12-mini",     "mini",     0, "256GB", 330000),
    ("12", 5, "iPhone 12",          "iphone-12",          "standard", 1, "64GB",  300000),
    ("12", 5, "iPhone 12",          "iphone-12",          "standard", 1, "128GB", 335000),
    ("12", 5, "iPhone 12",          "iphone-12",          "standard", 1, "256GB", 370000),
    ("12", 5, "iPhone 12 Pro",      "iphone-12-pro",      "pro",      2, "128GB", 370000),
    ("12", 5, "iPhone 12 Pro",      "iphone-12-pro",      "pro",      2, "256GB", 425000),
    ("12", 5, "iPhone 12 Pro",      "iphone-12-pro",      "pro",      2, "512GB", 475000),
    ("12", 5, "iPhone 12 Pro Max",  "iphone-12-pro-max",  "max",      3, "128GB", 400000),
    ("12", 5, "iPhone 12 Pro Max",  "iphone-12-pro-max",  "max",      3, "256GB", 450000),
    ("12", 5, "iPhone 12 Pro Max",  "iphone-12-pro-max",  "max",      3, "512GB", 510000),
    # ── iPhone 13 ─────────────────────────────────────────────────────────────
    ("13", 6, "iPhone 13 mini",     "iphone-13-mini",     "mini",     0, "128GB", 335000),
    ("13", 6, "iPhone 13 mini",     "iphone-13-mini",     "mini",     0, "256GB", 380000),
    ("13", 6, "iPhone 13 mini",     "iphone-13-mini",     "mini",     0, "512GB", 425000),
    ("13", 6, "iPhone 13",          "iphone-13",          "standard", 1, "128GB", 390000),
    ("13", 6, "iPhone 13",          "iphone-13",          "standard", 1, "256GB", 440000),
    ("13", 6, "iPhone 13",          "iphone-13",          "standard", 1, "512GB", 490000),
    ("13", 6, "iPhone 13 Pro",      "iphone-13-pro",      "pro",      2, "128GB", 460000),
    ("13", 6, "iPhone 13 Pro",      "iphone-13-pro",      "pro",      2, "256GB", 520000),
    ("13", 6, "iPhone 13 Pro",      "iphone-13-pro",      "pro",      2, "512GB", 580000),
    ("13", 6, "iPhone 13 Pro",      "iphone-13-pro",      "pro",      2, "1TB",   640000),
    ("13", 6, "iPhone 13 Pro Max",  "iphone-13-pro-max",  "max",      3, "128GB", 495000),
    ("13", 6, "iPhone 13 Pro Max",  "iphone-13-pro-max",  "max",      3, "256GB", 555000),
    ("13", 6, "iPhone 13 Pro Max",  "iphone-13-pro-max",  "max",      3, "512GB", 625000),
    ("13", 6, "iPhone 13 Pro Max",  "iphone-13-pro-max",  "max",      3, "1TB",   695000),
    # ── iPhone 14 ─────────────────────────────────────────────────────────────
    ("14", 7, "iPhone 14",          "iphone-14",          "standard", 0, "128GB",  500000),
    ("14", 7, "iPhone 14",          "iphone-14",          "standard", 0, "256GB",  560000),
    ("14", 7, "iPhone 14",          "iphone-14",          "standard", 0, "512GB",  620000),
    ("14", 7, "iPhone 14 Plus",     "iphone-14-plus",     "plus",     1, "128GB",  525000),
    ("14", 7, "iPhone 14 Plus",     "iphone-14-plus",     "plus",     1, "256GB",  585000),
    ("14", 7, "iPhone 14 Plus",     "iphone-14-plus",     "plus",     1, "512GB",  655000),
    ("14", 7, "iPhone 14 Pro",      "iphone-14-pro",      "pro",      2, "128GB",  600000),
    ("14", 7, "iPhone 14 Pro",      "iphone-14-pro",      "pro",      2, "256GB",  675000),
    ("14", 7, "iPhone 14 Pro",      "iphone-14-pro",      "pro",      2, "512GB",  745000),
    ("14", 7, "iPhone 14 Pro",      "iphone-14-pro",      "pro",      2, "1TB",    820000),
    ("14", 7, "iPhone 14 Pro Max",  "iphone-14-pro-max",  "max",      3, "128GB",  645000),
    ("14", 7, "iPhone 14 Pro Max",  "iphone-14-pro-max",  "max",      3, "256GB",  725000),
    ("14", 7, "iPhone 14 Pro Max",  "iphone-14-pro-max",  "max",      3, "512GB",  800000),
    ("14", 7, "iPhone 14 Pro Max",  "iphone-14-pro-max",  "max",      3, "1TB",    880000),
    # ── iPhone 15 ─────────────────────────────────────────────────────────────
    ("15", 8, "iPhone 15",          "iphone-15",          "standard", 0, "128GB",  620000),
    ("15", 8, "iPhone 15",          "iphone-15",          "standard", 0, "256GB",  695000),
    ("15", 8, "iPhone 15",          "iphone-15",          "standard", 0, "512GB",  760000),
    ("15", 8, "iPhone 15 Plus",     "iphone-15-plus",     "plus",     1, "128GB",  655000),
    ("15", 8, "iPhone 15 Plus",     "iphone-15-plus",     "plus",     1, "256GB",  725000),
    ("15", 8, "iPhone 15 Plus",     "iphone-15-plus",     "plus",     1, "512GB",  800000),
    ("15", 8, "iPhone 15 Pro",      "iphone-15-pro",      "pro",      2, "128GB",  740000),
    ("15", 8, "iPhone 15 Pro",      "iphone-15-pro",      "pro",      2, "256GB",  825000),
    ("15", 8, "iPhone 15 Pro",      "iphone-15-pro",      "pro",      2, "512GB",  915000),
    ("15", 8, "iPhone 15 Pro",      "iphone-15-pro",      "pro",      2, "1TB",   1015000),
    ("15", 8, "iPhone 15 Pro Max",  "iphone-15-pro-max",  "max",      3, "256GB",  905000),
    ("15", 8, "iPhone 15 Pro Max",  "iphone-15-pro-max",  "max",      3, "512GB", 1000000),
    ("15", 8, "iPhone 15 Pro Max",  "iphone-15-pro-max",  "max",      3, "1TB",   1120000),
    # ── iPhone 16 ─────────────────────────────────────────────────────────────
    ("16", 9, "iPhone 16",          "iphone-16",          "standard", 0, "128GB",  775000),
    ("16", 9, "iPhone 16",          "iphone-16",          "standard", 0, "256GB",  860000),
    ("16", 9, "iPhone 16",          "iphone-16",          "standard", 0, "512GB",  950000),
    ("16", 9, "iPhone 16 Plus",     "iphone-16-plus",     "plus",     1, "128GB",  820000),
    ("16", 9, "iPhone 16 Plus",     "iphone-16-plus",     "plus",     1, "256GB",  915000),
    ("16", 9, "iPhone 16 Plus",     "iphone-16-plus",     "plus",     1, "512GB", 1010000),
    ("16", 9, "iPhone 16 Pro",      "iphone-16-pro",      "pro",      2, "128GB",  950000),
    ("16", 9, "iPhone 16 Pro",      "iphone-16-pro",      "pro",      2, "256GB", 1055000),
    ("16", 9, "iPhone 16 Pro",      "iphone-16-pro",      "pro",      2, "512GB", 1165000),
    ("16", 9, "iPhone 16 Pro",      "iphone-16-pro",      "pro",      2, "1TB",   1295000),
    ("16", 9, "iPhone 16 Pro Max",  "iphone-16-pro-max",  "max",      3, "256GB", 1080000),
    ("16", 9, "iPhone 16 Pro Max",  "iphone-16-pro-max",  "max",      3, "512GB", 1210000),
    ("16", 9, "iPhone 16 Pro Max",  "iphone-16-pro-max",  "max",      3, "1TB",   1380000),
    # ── iPhone 17 ─────────────────────────────────────────────────────────────
    ("17", 10, "iPhone 17",         "iphone-17",          "standard", 0, "128GB", 860000),
    ("17", 10, "iPhone 17",         "iphone-17",          "standard", 0, "256GB", 950000),
    ("17", 10, "iPhone 17",         "iphone-17",          "standard", 0, "512GB", 1045000),
    ("17", 10, "iPhone 17 Air",     "iphone-17-air",      "air",      1, "128GB",  905000),
    ("17", 10, "iPhone 17 Air",     "iphone-17-air",      "air",      1, "256GB", 1000000),
    ("17", 10, "iPhone 17 Air",     "iphone-17-air",      "air",      1, "512GB", 1105000),
    ("17", 10, "iPhone 17 Pro",     "iphone-17-pro",      "pro",      2, "128GB", 1055000),
    ("17", 10, "iPhone 17 Pro",     "iphone-17-pro",      "pro",      2, "256GB", 1165000),
    ("17", 10, "iPhone 17 Pro",     "iphone-17-pro",      "pro",      2, "512GB", 1295000),
    ("17", 10, "iPhone 17 Pro",     "iphone-17-pro",      "pro",      2, "1TB",   1440000),
    ("17", 10, "iPhone 17 Pro Max", "iphone-17-pro-max",  "max",      3, "256GB", 1210000),
    ("17", 10, "iPhone 17 Pro Max", "iphone-17-pro-max",  "max",      3, "512GB", 1345000),
    ("17", 10, "iPhone 17 Pro Max", "iphone-17-pro-max",  "max",      3, "1TB",   1510000),
    ("17", 10, "iPhone 17 Pro Max", "iphone-17-pro-max",  "max",      3, "2TB",   1690000),
    # ── iPhone SE ─────────────────────────────────────────────────────────────
    ("SE", 11, "iPhone SE (1st gen)", "iphone-se-1st-gen", "standard", 0, "16GB",  40000),
    ("SE", 11, "iPhone SE (1st gen)", "iphone-se-1st-gen", "standard", 0, "32GB",  45000),
    ("SE", 11, "iPhone SE (1st gen)", "iphone-se-1st-gen", "standard", 0, "64GB",  50000),
    ("SE", 11, "iPhone SE (2nd gen)", "iphone-se-2nd-gen", "standard", 1, "64GB",  165000),
    ("SE", 11, "iPhone SE (2nd gen)", "iphone-se-2nd-gen", "standard", 1, "128GB", 190000),
    ("SE", 11, "iPhone SE (2nd gen)", "iphone-se-2nd-gen", "standard", 1, "256GB", 220000),
    ("SE", 11, "iPhone SE (3rd gen)", "iphone-se-3rd-gen", "standard", 2, "64GB",  175000),
    ("SE", 11, "iPhone SE (3rd gen)", "iphone-se-3rd-gen", "standard", 2, "128GB", 200000),
    ("SE", 11, "iPhone SE (3rd gen)", "iphone-se-3rd-gen", "standard", 2, "256GB", 225000),
]


HEADER = [
    "series_name", "series_order", "model_name", "model_slug",
    "variant_type", "model_order", "capacity",
    "swap_in_value_ngn", "uk_end_user_price_ngn",
    "uk_reseller_price_ngn", "ng_end_user_price_ngn", "ng_reseller_price_ngn",
]

with open(OUT / "iphone_catalog.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(HEADER)
    for row in ROWS:
        series_name, series_order, model_name, model_slug, variant_type, model_order, capacity, uk_reseller = row
        p = compute_prices(model_slug, uk_reseller)
        w.writerow([
            series_name, series_order, model_name, model_slug,
            variant_type, model_order, capacity,
            p["swap_in"], p["uk_end"], p["uk_reseller"], p["ng_end"], p["ng_reseller"],
        ])

print(f"iphone_catalog.csv written ({len(ROWS)} rows)")
