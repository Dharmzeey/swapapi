"""
Run with plain Python (not Django):
    python data/generate_defects.py

Produces:
    data/defect_types.csv
    data/defect_pricing.csv
"""

import csv
from pathlib import Path

OUT = Path(__file__).parent

# ── Defect types ───────────────────────────────────────────────────────────────
# default_deduction_pct = base rate used for all non-pro-max models
DEFECT_TYPES = [
    # slug, name, category, default_deduction_pct, description, applies_to_view, order
    ("broken-screen",          "Broken Screen",                     "damage",        20, "Cracked or shattered display glass",                                        "front", 0),
    ("broken-back-glass",      "Broken Back Glass",                 "damage",         5, "Cracked or shattered rear glass panel",                                     "back",  1),
    ("cracked-camera-glass",   "Cracked Camera Glass",              "damage",         4, "Cracked glass over rear camera module",                                     "back",  2),
    ("rough-body",             "Rough Body / Dents",                "damage",        10, "Visible dents, scratches or scuffs on frame or body",                      "both",  3),
    ("bent-frame",             "Bent Frame",                        "damage",        10, "Visibly bent or warped chassis",                                            "both",  4),
    ("face-id-fault",          "Face ID Not Working",               "functional",    25, "Face ID biometric sensor is non-functional (typically irreparable)",        "front", 5),
    ("touch-id-fault",         "Touch ID Not Working",              "functional",    15, "Home button fingerprint sensor is non-functional (typically irreparable)",  "front", 6),
    ("faulty-charging-port",   "Faulty Charging Port",              "functional",     8, "Charging port does not charge reliably or is physically damaged",           "both",  7),
    ("faulty-rear-camera",     "Faulty Rear Camera",                "functional",    11, "One or more rear cameras are non-functional or produce poor images",        "back",  8),
    ("faulty-front-camera",    "Faulty Front Camera",               "functional",    10, "Front-facing camera is non-functional or produces poor images",             "front", 9),
    ("battery-degraded",       "Battery Degraded",                  "functional",     8, "Battery health below 80% or battery is swollen",                           "both",  10),
    ("speaker-mic-fault",      "Speaker / Microphone Fault",        "functional",     7, "Earpiece, loudspeaker or microphone not working correctly",                 "both",  11),
    ("wifi-bluetooth-fault",   "Wi-Fi / Bluetooth Fault",           "functional",    10, "Wi-Fi or Bluetooth connectivity issues",                                    "both",  12),
    ("water-damage",           "Water Damage",                      "functional",    30, "Liquid Contact Indicator triggered or internal corrosion visible",          "both",  13),
    ("screen-replaced",        "Screen Replaced (Non-Original)",    "replaced_part", 12, "Display has been replaced with a non-Apple original part",                 "front", 14),
    ("battery-replaced",       "Battery Replaced",                  "replaced_part",  8, "Battery has been replaced (original or third-party)",                      "both",  15),
    ("back-glass-replaced",    "Back Glass Replaced (Non-Original)","replaced_part",  5, "Rear glass panel has been replaced with a non-original part",              "back",  16),
    ("camera-replaced",        "Camera Replaced (Non-Original)",    "replaced_part", 10, "Rear camera module has been replaced with a non-original part",            "back",  17),
    ("charging-port-replaced", "Charging Port Replaced",            "replaced_part",  5, "Charging port has been replaced",                                          "both",  18),
]

# Quick lookup: slug → default_deduction_pct
DEFECT_BASE_PCT = {r[0]: r[3] for r in DEFECT_TYPES}

# Defects that have NO repair cost (irreparable / no physical fix)
NO_REPAIR_COST = {
    "face-id-fault",
    "touch-id-fault",
    "wifi-bluetooth-fault",
    "water-damage",
    "screen-replaced",
    "battery-replaced",
    "back-glass-replaced",
    "camera-replaced",
    "charging-port-replaced",
}

# ── Model groups ───────────────────────────────────────────────────────────────
# OLD = series 6 through 13 (incl. X / SE) → flat repair 3 000
OLD_MODELS = [
    "iphone-6", "iphone-6-plus", "iphone-6s", "iphone-6s-plus",
    "iphone-se-1st-gen",
    "iphone-7", "iphone-7-plus", "iphone-8", "iphone-8-plus",
    "iphone-se-2nd-gen",
    "iphone-x", "iphone-xs", "iphone-xr",
    "iphone-xs-max",
    "iphone-11", "iphone-11-pro", "iphone-11-pro-max",
    "iphone-se-3rd-gen",
    "iphone-12-mini", "iphone-12", "iphone-12-pro", "iphone-12-pro-max",
    "iphone-13-mini", "iphone-13", "iphone-13-pro", "iphone-13-pro-max",
]

# NEW = series 14 through 17 → flat repair 5 000
NEW_MODELS = [
    "iphone-14", "iphone-14-plus", "iphone-14-pro", "iphone-14-pro-max",
    "iphone-15", "iphone-15-plus", "iphone-15-pro", "iphone-15-pro-max",
    "iphone-16", "iphone-16-plus", "iphone-16-pro", "iphone-16-pro-max",
    "iphone-17", "iphone-17-air", "iphone-17-pro", "iphone-17-pro-max",
]

ALL_MODELS = OLD_MODELS + NEW_MODELS

# Pro Max models get deduction_pct + 1 % on every non-zero defect
PRO_MAX = {
    "iphone-xs-max",
    "iphone-11-pro-max",
    "iphone-12-pro-max",
    "iphone-13-pro-max",
    "iphone-14-pro-max",
    "iphone-15-pro-max",
    "iphone-16-pro-max",
    "iphone-17-pro-max",
}

# Models that use Touch ID (no Face ID)
NO_FACE_ID = {
    "iphone-6", "iphone-6-plus", "iphone-6s", "iphone-6s-plus",
    "iphone-se-1st-gen",
    "iphone-7", "iphone-7-plus", "iphone-8", "iphone-8-plus",
    "iphone-se-2nd-gen",
    "iphone-se-3rd-gen",
}

# Models that use Face ID (no Touch ID)
NO_TOUCH_ID = set(ALL_MODELS) - NO_FACE_ID


# ── Write defect_types.csv ─────────────────────────────────────────────────────
with open(OUT / "defect_types.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["slug", "name", "category", "default_deduction_pct",
                "description", "applies_to_view", "order"])
    for row in DEFECT_TYPES:
        w.writerow(row)

print(f"defect_types.csv written ({len(DEFECT_TYPES)} rows)")


# ── Write defect_pricing.csv ───────────────────────────────────────────────────
rows = []
for r in DEFECT_TYPES:
    defect_slug = r[0]
    base_pct    = r[3]

    for model_slug in ALL_MODELS:
        # --- deduction_pct ---
        if defect_slug == "face-id-fault" and model_slug in NO_FACE_ID:
            deduction = 0
        elif defect_slug == "touch-id-fault" and model_slug in NO_TOUCH_ID:
            deduction = 0
        else:
            deduction = base_pct
            if model_slug in PRO_MAX and deduction > 0:
                deduction += 1

        # --- repair_cost ---
        if defect_slug in NO_REPAIR_COST:
            repair = 0
        elif model_slug in OLD_MODELS:
            repair = 3000
        else:
            repair = 5000

        rows.append((model_slug, defect_slug, deduction, repair))

with open(OUT / "defect_pricing.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["model_slug", "defect_slug", "deduction_pct", "repair_cost_ngn"])
    for row in rows:
        w.writerow(row)

print(f"defect_pricing.csv written ({len(rows)} rows)")
