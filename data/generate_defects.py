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

# ── Defect types ──────────────────────────────────────────────────────────────
DEFECT_TYPES = [
    # slug, name, category, default_deduction_pct, description, applies_to_view, order
    ("broken-screen",          "Broken Screen",                    "damage",        20, "Cracked or shattered display glass",                                           "front", 0),
    ("broken-back-glass",      "Broken Back Glass",                "damage",        15, "Cracked or shattered rear glass panel",                                        "back",  1),
    ("cracked-camera-glass",   "Cracked Camera Glass",             "damage",         8, "Cracked glass over rear camera module",                                        "back",  2),
    ("rough-body",             "Rough Body / Dents",               "damage",         5, "Visible dents, scratches or scuffs on frame or body",                         "both",  3),
    ("bent-frame",             "Bent Frame",                       "damage",        10, "Visibly bent or warped chassis",                                               "both",  4),
    ("face-id-fault",          "Face ID Not Working",              "functional",    25, "Face ID biometric sensor is non-functional (typically irreparable)",           "front", 5),
    ("touch-id-fault",         "Touch ID Not Working",             "functional",    15, "Home button fingerprint sensor is non-functional (typically irreparable)",     "front", 6),
    ("faulty-charging-port",   "Faulty Charging Port",             "functional",    10, "Charging port does not charge reliably or is physically damaged",              "both",  7),
    ("faulty-rear-camera",     "Faulty Rear Camera",               "functional",    12, "One or more rear cameras are non-functional or produce poor images",           "back",  8),
    ("faulty-front-camera",    "Faulty Front Camera",              "functional",     8, "Front-facing camera is non-functional or produces poor images",                "front", 9),
    ("battery-degraded",       "Battery Degraded",                 "functional",     8, "Battery health below 80% or battery is swollen",                              "both",  10),
    ("speaker-mic-fault",      "Speaker / Microphone Fault",       "functional",     7, "Earpiece, loudspeaker or microphone not working correctly",                    "both",  11),
    ("wifi-bluetooth-fault",   "Wi-Fi / Bluetooth Fault",          "functional",    10, "Wi-Fi or Bluetooth connectivity issues",                                       "both",  12),
    ("water-damage",           "Water Damage",                     "functional",    20, "Liquid Contact Indicator triggered or internal corrosion visible",             "both",  13),
    ("screen-replaced",        "Screen Replaced (Non-Original)",   "replaced_part", 12, "Display has been replaced with a non-Apple original part",                    "front", 14),
    ("battery-replaced",       "Battery Replaced",                 "replaced_part",  8, "Battery has been replaced (original or third-party)",                         "both",  15),
    ("back-glass-replaced",    "Back Glass Replaced (Non-Original)","replaced_part", 8, "Rear glass panel has been replaced with a non-original part",                 "back",  16),
    ("camera-replaced",        "Camera Replaced (Non-Original)",   "replaced_part", 10, "Rear camera module has been replaced with a non-original part",               "back",  17),
    ("charging-port-replaced", "Charging Port Replaced",           "replaced_part",  5, "Charging port has been replaced",                                             "both",  18),
]

# ── Model tiers ───────────────────────────────────────────────────────────────
# Tier key → list of model slugs
TIERS = {
    1: ["iphone-6", "iphone-6-plus", "iphone-6s", "iphone-6s-plus", "iphone-se-1st-gen"],
    2: ["iphone-7", "iphone-7-plus", "iphone-8", "iphone-8-plus", "iphone-se-2nd-gen"],
    # 3  = Face ID models starting from iPhone X
    3: ["iphone-x", "iphone-xs", "iphone-xr", "iphone-11"],
    # 3t = SE 3rd gen — same price range as T3 but has Touch ID, not Face ID
    "3t": ["iphone-se-3rd-gen"],
    4: ["iphone-xs-max", "iphone-11-pro", "iphone-11-pro-max", "iphone-12-mini", "iphone-12"],
    5: ["iphone-12-pro", "iphone-12-pro-max", "iphone-13-mini", "iphone-13",
        "iphone-13-pro", "iphone-13-pro-max"],
    6: ["iphone-14", "iphone-14-plus", "iphone-14-pro", "iphone-14-pro-max",
        "iphone-15", "iphone-15-plus"],
    7: ["iphone-15-pro", "iphone-15-pro-max",
        "iphone-16", "iphone-16-plus", "iphone-16-pro", "iphone-16-pro-max",
        "iphone-17", "iphone-17-air", "iphone-17-pro", "iphone-17-pro-max"],
}

# Models without Face ID (= Touch ID or no biometrics)
NO_FACE_ID = set(TIERS[1] + TIERS[2] + TIERS["3t"])
# Models without Touch ID (= Face ID)
NO_TOUCH_ID = set(TIERS[3] + TIERS[4] + TIERS[5] + TIERS[6] + TIERS[7])

# ── Pricing matrix ────────────────────────────────────────────────────────────
# Format per tier key: (deduction_pct, repair_cost_ngn)
PRICING = {
    #                            T1           T2           T3           T3t          T4           T5           T6           T7
    "broken-screen":          {1:(20,15000), 2:(20,22000), 3:(22,32000),"3t":(22,32000), 4:(22,48000), 5:(23,62000), 6:(23,78000), 7:(25,95000)},
    "broken-back-glass":      {1:(12, 8000), 2:(13,13000), 3:(15,20000),"3t":(15,20000), 4:(15,28000), 5:(16,38000), 6:(16,48000), 7:(18,60000)},
    "cracked-camera-glass":   {1:( 5, 3000), 2:( 5, 5000), 3:( 6, 8000),"3t":( 6, 8000), 4:( 7,12000), 5:( 7,15000), 6:( 8,20000), 7:( 8,25000)},
    "rough-body":             {1:( 5, 5000), 2:( 5, 7000), 3:( 5, 9000),"3t":( 5, 9000), 4:( 5,11000), 5:( 5,13000), 6:( 5,16000), 7:( 5,20000)},
    "bent-frame":             {1:(10, 8000), 2:(10,13000), 3:(12,20000),"3t":(12,20000), 4:(12,25000), 5:(12,30000), 6:(12,38000), 7:(15,48000)},
    # face-id: 0,0 for models that have Touch ID instead
    "face-id-fault":          {1:( 0,    0), 2:( 0,    0), 3:(25,    0),"3t":( 0,    0), 4:(25,    0), 5:(28,    0), 6:(28,    0), 7:(30,    0)},
    # touch-id: 0,0 for models that have Face ID instead
    "touch-id-fault":         {1:(15,    0), 2:(15,    0), 3:( 0,    0),"3t":(15,    0), 4:( 0,    0), 5:( 0,    0), 6:( 0,    0), 7:( 0,    0)},
    "faulty-charging-port":   {1:( 8, 8000), 2:( 8,12000), 3:(10,16000),"3t":(10,16000), 4:(10,20000), 5:(10,24000), 6:(10,28000), 7:(10,32000)},
    "faulty-rear-camera":     {1:(10,10000), 2:(10,15000), 3:(12,22000),"3t":(12,22000), 4:(12,32000), 5:(13,42000), 6:(13,55000), 7:(15,70000)},
    "faulty-front-camera":    {1:( 7, 8000), 2:( 7,10000), 3:( 8,14000),"3t":( 8,14000), 4:( 8,18000), 5:( 8,22000), 6:( 8,27000), 7:( 8,32000)},
    "battery-degraded":       {1:( 8, 8000), 2:( 8,10000), 3:( 8,14000),"3t":( 8,14000), 4:( 8,16000), 5:( 8,18000), 6:( 8,22000), 7:( 8,25000)},
    "speaker-mic-fault":      {1:( 6, 6000), 2:( 6, 8000), 3:( 7,11000),"3t":( 7,11000), 4:( 7,14000), 5:( 7,17000), 6:( 7,20000), 7:( 7,24000)},
    "wifi-bluetooth-fault":   {1:( 8,    0), 2:( 8,    0), 3:(10,    0),"3t":(10,    0), 4:(10,    0), 5:(10,    0), 6:(10,    0), 7:(10,    0)},
    "water-damage":           {1:(20,    0), 2:(20,    0), 3:(22,    0),"3t":(22,    0), 4:(22,    0), 5:(22,    0), 6:(22,    0), 7:(25,    0)},
    "screen-replaced":        {1:(10,    0), 2:(10,    0), 3:(12,    0),"3t":(12,    0), 4:(12,    0), 5:(12,    0), 6:(12,    0), 7:(12,    0)},
    "battery-replaced":       {1:( 6,    0), 2:( 6,    0), 3:( 8,    0),"3t":( 8,    0), 4:( 8,    0), 5:( 8,    0), 6:( 8,    0), 7:( 8,    0)},
    "back-glass-replaced":    {1:( 8,    0), 2:( 8,    0), 3:(10,    0),"3t":(10,    0), 4:(10,    0), 5:(10,    0), 6:(10,    0), 7:(10,    0)},
    "camera-replaced":        {1:( 8,    0), 2:( 8,    0), 3:(10,    0),"3t":(10,    0), 4:(10,    0), 5:(10,    0), 6:(10,    0), 7:(10,    0)},
    "charging-port-replaced": {1:( 4,    0), 2:( 4,    0), 3:( 5,    0),"3t":( 5,    0), 4:( 5,    0), 5:( 5,    0), 6:( 5,    0), 7:( 5,    0)},
}

# ── Write defect_types.csv ────────────────────────────────────────────────────
with open(OUT / "defect_types.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["slug", "name", "category", "default_deduction_pct", "description", "applies_to_view", "order"])
    for row in DEFECT_TYPES:
        w.writerow(row)

print(f"defect_types.csv written ({len(DEFECT_TYPES)} rows)")

# ── Write defect_pricing.csv ──────────────────────────────────────────────────
rows = []
for defect_slug, tier_pricing in PRICING.items():
    for tier_key, slugs in TIERS.items():
        deduction, repair = tier_pricing[tier_key]
        for model_slug in slugs:
            rows.append((model_slug, defect_slug, deduction, repair))

with open(OUT / "defect_pricing.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["model_slug", "defect_slug", "deduction_pct", "repair_cost_ngn"])
    for row in rows:
        w.writerow(row)

print(f"defect_pricing.csv written ({len(rows)} rows)")
