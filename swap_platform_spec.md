# SwapEstimator — Django Project Specification

## Project Overview

A web platform where customers configure an iPhone they want to swap **from**, specify defects, pick the iPhone they want to swap **to**, and receive an instant price estimate in Nigerian Naira — showing how much they owe (upgrade) or receive (downgrade).

---

## App Structure

```
swap_estimator/          ← Django project root
├── core/                ← main app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py   ← if using DRF for API responses
│   ├── admin.py
│   └── templates/
│       └── core/
│           ├── index.html          ← landing / selector
│           ├── configurator.html   ← defect + swap-to picker
│           └── estimate.html       ← price result
├── static/
│   ├── css/
│   └── js/
└── swap_estimator/
    ├── settings.py
    └── urls.py
```

---

## Models

### 1. `IphoneSeries`
Represents a major iPhone generation (X, 11, 12 … 17).

```
Fields:
- id          AutoField PK
- name        CharField       e.g. "X", "11", "12", "13", "14", "15", "16", "17"
- order       PositiveIntegerField   for sorting in the UI (X=0, 11=1 … 17=7)
- is_active   BooleanField default True
```

---

### 2. `IphoneModel`
Represents a specific sub-model within a series (XR, XS Max, 13 Pro Max, etc.).

```
Fields:
- id            AutoField PK
- series        ForeignKey → IphoneSeries (on_delete=CASCADE)
- name          CharField   e.g. "iPhone XR", "iPhone 13 Pro Max"
- slug          SlugField   e.g. "iphone-xr", "iphone-13-pro-max"
- variant_type  CharField   choices: standard | mini | plus | pro | max | air
- order         PositiveIntegerField   sort within series
- is_active     BooleanField default True
```

**`variant_type` choices reference:**

| Series | Variants |
|--------|----------|
| X | standard (X), standard (XR), pro (XS), max (XS Max) |
| 11 | standard, pro, max |
| 12–13 | mini, standard, pro, max |
| 14–16 | standard, plus, pro, max |
| 17 | standard, air, pro, max |

---

### 3. `StorageVariant`
Storage options per model with a base trade-in value in Naira.

```
Fields:
- id              AutoField PK
- model           ForeignKey → IphoneModel (on_delete=CASCADE)
- capacity        CharField   choices: 64GB | 128GB | 256GB | 512GB | 1TB
- base_value_ngn  DecimalField(max_digits=12, decimal_places=2)
                  ← trade-in value for a PERFECT condition device
- is_active       BooleanField default True
```

> `base_value_ngn` is the anchor for all pricing math.
> Admin updates this field as market rates shift.

---

### 4. `DefectType`
Catalogue of defects a customer can declare on their swap-from device.

```
Fields:
- id              AutoField PK
- name            CharField   e.g. "Cracked Screen", "No Face ID"
- slug            SlugField   e.g. "cracked-screen", "no-face-id"
- description     TextField   short UI help text
- deduction_pct   DecimalField(max_digits=5, decimal_places=2)
                  ← percentage deducted from base_value_ngn
- applies_to_view CharField   choices: front | back | both
                  ← controls which phone face renders the overlay
- order           PositiveIntegerField
- is_active       BooleanField default True
```

**Seed data (defects + suggested deduction %):**

| Defect | Slug | Deduction |
|--------|------|-----------|
| No Face ID | no-face-id | 15% |
| Changed Battery | changed-battery | 8% |
| Changed Screen | changed-screen | 10% |
| Changed Camera | changed-camera | 12% |
| Cracked / Broken Screen | cracked-screen | 25% |
| Cracked / Broken Back Glass | cracked-back | 15% |
| Rough Body / Frame | rough-body | 10% |

> Deductions stack multiplicatively, not additively, to prevent the value going negative.
> Formula: `final_value = base_value × ∏(1 - deduction_i)`

---

### 5. `SwapEstimate` *(optional — for logging / analytics)*
Records each estimate session for business analytics and rate tuning.

```
Fields:
- id                  AutoField PK
- session_key         CharField   ← Django session key, links anonymous users
- from_storage        ForeignKey → StorageVariant (related_name='swap_from')
- to_storage          ForeignKey → StorageVariant (related_name='swap_to')
- defects             ManyToManyField → DefectType (blank=True)
- from_value_ngn      DecimalField   ← computed trade-in after deductions
- to_value_ngn        DecimalField   ← base_value of target device
- service_fee_ngn     DecimalField   ← flat fee (set in settings)
- net_amount_ngn      DecimalField   ← positive = customer pays, negative = customer receives
- created_at          DateTimeField auto_now_add=True
```

> This model is optional for MVP. Add it when you want to track demand, popular combos, and adjust prices based on real usage.

---

## Views

### `HomeView` — `GET /`
- Renders `index.html`
- Passes all active `IphoneSeries` ordered by `order`
- No DB-heavy queries; series list is small and can be cached

---

### `GetModelsView` — `GET /api/models/<series_id>/`
- Returns JSON list of active `IphoneModel` objects for the given series
- Each object includes `id`, `name`, `slug`, `variant_type`
- Used by frontend JS when user picks a series (AJAX / fetch call)

---

### `GetStorageView` — `GET /api/storage/<model_id>/`
- Returns JSON list of active `StorageVariant` objects for the given model
- Each object includes `id`, `capacity`, `base_value_ngn`
- Used by frontend JS when user picks a sub-model

---

### `GetDefectsView` — `GET /api/defects/`
- Returns full list of active `DefectType` objects
- Called once on page load; client caches it in JS state
- Fields: `id`, `name`, `slug`, `description`, `deduction_pct`, `applies_to_view`

---

### `EstimateView` — `POST /estimate/`
Core business logic view.

**Request body (JSON or form POST):**
```json
{
  "from_storage_id": 12,
  "to_storage_id": 34,
  "defect_ids": [1, 3, 5]
}
```

**Logic:**
```python
from_storage  = StorageVariant.objects.get(pk=from_storage_id)
to_storage    = StorageVariant.objects.get(pk=to_storage_id)
defects       = DefectType.objects.filter(pk__in=defect_ids)

# Multiplicative deduction
from_value = from_storage.base_value_ngn
for defect in defects:
    from_value *= (1 - defect.deduction_pct / 100)

to_value     = to_storage.base_value_ngn
service_fee  = Decimal(settings.SWAP_SERVICE_FEE_NGN)   # e.g. 10000
net          = (to_value - from_value) + service_fee
              # positive → customer pays
              # negative → customer receives cashback
```

**Response (JSON):**
```json
{
  "from_device": "iPhone 13 · 128GB",
  "from_value_ngn": 285000.00,
  "to_device": "iPhone 15 Pro · 256GB",
  "to_value_ngn": 680000.00,
  "service_fee_ngn": 10000.00,
  "net_ngn": 405000.00,
  "direction": "upgrade",
  "defects_applied": ["Cracked Screen", "Changed Battery"]
}
```

`direction` is `"upgrade"` (pay), `"downgrade"` (receive), or `"even"`.

---

### `ConfiguratorView` — `GET /configure/` *(optional server-rendered version)*
- Alternative to pure AJAX: renders `configurator.html` with all series, defects, and JS data pre-loaded in a `<script>` tag as JSON
- Reduces round trips on slow connections

---

## Admin Configuration

Register all models in `admin.py`. Key customisations:

- `StorageVariant`: list_display = model name, capacity, base_value_ngn, is_active. Allow inline editing of `base_value_ngn` so prices can be updated without code changes.
- `DefectType`: list_display = name, deduction_pct, applies_to_view, order. Editable `deduction_pct` inline.
- `IphoneModel`: inline `StorageVariant` stacked inline under each model.

---

## Settings to Add

```python
# swap_estimator/settings.py

SWAP_SERVICE_FEE_NGN = 10_000   # flat service charge per swap estimate

# Optional: cache defects + series lists (they rarely change)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

---

## URL Patterns

```python
# core/urls.py
urlpatterns = [
    path("",                          HomeView.as_view(),        name="home"),
    path("configure/",                ConfiguratorView.as_view(),name="configurator"),
    path("estimate/",                 EstimateView.as_view(),    name="estimate"),
    path("api/models/<int:series_id>/", GetModelsView.as_view(), name="api-models"),
    path("api/storage/<int:model_id>/", GetStorageView.as_view(),name="api-storage"),
    path("api/defects/",              GetDefectsView.as_view(),  name="api-defects"),
]
```

---

## Data Flow Summary

```
User lands on /
    → JS loads IphoneSeries from page context
    → User picks series → GET /api/models/<id>/ → render sub-models
    → User picks sub-model → GET /api/storage/<id>/ → render storage buttons
    → User selects storage (SWAP FROM confirmed)
    → User picks defects (checkboxes, visual overlay updates)
    → User picks SWAP TO series → model → storage (same AJAX flow, no defects)
    → User clicks "Get Estimate"
    → POST /estimate/ with from_storage_id, to_storage_id, defect_ids[]
    → Response rendered in estimate panel (no page reload)
```

---

## Notes for Implementation

- All prices stored and returned in **Naira (NGN)**. No currency conversion needed at this stage.
- `base_value_ngn` in `StorageVariant` is the only field that needs regular admin updates as market prices shift. Build the admin to make this as easy as possible.
- The defect deduction formula uses **multiplicative stacking** — this prevents edge cases where heavy defects push value below zero.
- For MVP, `SwapEstimate` logging is optional but worth adding early since pricing decisions will need real usage data.
- Keep the API views simple and stateless — no auth required for estimate queries at MVP stage.
