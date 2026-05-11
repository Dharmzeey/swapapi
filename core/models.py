from django.db import models


class IphoneSeries(models.Model):
    name = models.CharField(max_length=20)  # e.g. "6", "7", "8", "X", "11" ... "17", "SE"
    order = models.PositiveIntegerField()   # 6=0, 7=1, 8=2, X=3, 11=4, 12=5, 13=6, 14=7, 15=8, 16=9, 17=10, SE=11
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "iPhone Series"
        ordering = ["order"]

    def __str__(self):
        return f"iPhone {self.name}"


class IphoneModel(models.Model):
    class VariantType(models.TextChoices):
        STANDARD = "standard", "Standard"
        S = "s", "S"
        S_PLUS = "s-plus", "S Plus"
        MINI = "mini", "Mini"
        PLUS = "plus", "Plus"
        PRO = "pro", "Pro"
        MAX = "max", "Max"
        AIR = "air", "Air"
        XR = "xr", "XR"

    series = models.ForeignKey(IphoneSeries, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=60)    # e.g. "iPhone 13 Pro Max"
    slug = models.SlugField(unique=True)       # e.g. "iphone-13-pro-max"
    variant_type = models.CharField(max_length=10, choices=VariantType.choices)
    order = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["series__order", "order"]

    def __str__(self):
        return self.name


class StorageVariant(models.Model):
    class Capacity(models.TextChoices):
        GB_32 = "32GB", "32 GB"
        GB_64 = "64GB", "64 GB"
        GB_128 = "128GB", "128 GB"
        GB_256 = "256GB", "256 GB"
        GB_512 = "512GB", "512 GB"
        TB_1 = "1TB", "1 TB"
        TB_2 = "2TB", "2 TB"

    model = models.ForeignKey(IphoneModel, on_delete=models.CASCADE, related_name="storage_variants")
    capacity = models.CharField(max_length=10, choices=Capacity.choices)
    swap_in_value_ngn = models.PositiveIntegerField(
        help_text="What the shop pays when accepting this used phone (NGN). Update as market rates shift.",
    )
    uk_end_user_price_ngn = models.PositiveIntegerField(
        help_text="UK-condition end-user market price (NGN). Used as the swap-to price in estimates.",
    )
    uk_reseller_price_ngn = models.PositiveIntegerField(
        help_text="UK-condition reseller price (NGN).",
        null=True,
        blank=True,
    )
    ng_end_user_price_ngn = models.PositiveIntegerField(
        help_text="Nigerian-used end-user price after shop refurbishment (NGN).",
        null=True,
        blank=True,
    )
    ng_reseller_price_ngn = models.PositiveIntegerField(
        help_text="Nigerian-used reseller price (NGN).",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("model", "capacity")
        ordering = ["model__order", "capacity"]

    def __str__(self):
        return f"{self.model.name} · {self.capacity}"


class DefectType(models.Model):
    """
    A single type of defect or condition issue a customer can declare.

    Categories
    ----------
    damage        – physical damage the shop must repair (cracked screen, back glass, etc.)
    functional    – hardware/software faults (Face ID, charging port, etc.)
    replaced_part – non-original parts already fitted (battery, screen, camera, etc.)

    Pricing
    -------
    default_deduction_pct is the fallback % knocked off the base trade-in value when no
    per-model DefectPricing row exists.  For most defects a per-model row SHOULD be added
    because repair costs and value impact differ across generations.
    """

    class Category(models.TextChoices):
        DAMAGE = "damage", "Physical Damage"
        FUNCTIONAL = "functional", "Functional Issue"
        REPLACED_PART = "replaced_part", "Replaced Part"

    class AppliesTo(models.TextChoices):
        FRONT = "front", "Front"
        BACK = "back", "Back"
        BOTH = "both", "Both"

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    default_deduction_pct = models.PositiveIntegerField(
        help_text=(
            "Fallback % deducted from base_value_ngn when no per-model DefectPricing "
            "row exists. Multiplicative stacking: final = base × ∏(1 − pct/100)."
        ),
    )
    applies_to_view = models.CharField(
        max_length=5,
        choices=AppliesTo.choices,
        default=AppliesTo.BOTH,
        help_text="Controls which phone face shows the damage overlay in the UI.",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} (default -{self.default_deduction_pct} %)"


class DefectPricing(models.Model):
    """
    Per-model repair cost and value deduction for a specific defect.

    Why per-model?
    --------------
    Replacing a screen on an iPhone 16 Pro Max costs far more in parts and labour
    than on an iPhone 11. This table lets the admin maintain up-to-date costs for
    each combination without touching code.

    How it is used in the estimate
    --------------------------------
    For each declared defect on the swap-from phone:
      1. Look up this table for (defect, iphone_model).
      2. If found and active: use deduction_pct + repair_cost_ngn from this row.
      3. If not found: use defect.default_deduction_pct + 0 repair cost.

    The repair_cost_ngn is ADDED to the amount the customer owes (upgrade) or
    subtracted from the cashback they receive (downgrade).  It represents the shop's
    cost to bring the phone to sellable condition.
    """

    defect = models.ForeignKey(
        DefectType,
        on_delete=models.CASCADE,
        related_name="pricing",
    )
    iphone_model = models.ForeignKey(
        IphoneModel,
        on_delete=models.CASCADE,
        related_name="defect_pricing",
    )
    deduction_pct = models.PositiveIntegerField(
        help_text="% deducted from this model's base_value_ngn for this defect.",
    )
    repair_cost_ngn = models.PositiveIntegerField(
        help_text=(
            "Cost (NGN) to repair or replace this part on this model. "
            "Added on top of the swap difference — update whenever parts/labour prices change."
        ),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("defect", "iphone_model")
        ordering = ["iphone_model__series__order", "iphone_model__order", "defect__order"]
        verbose_name = "Defect Pricing"
        verbose_name_plural = "Defect Pricing"

    def __str__(self):
        return (
            f"{self.defect.name} on {self.iphone_model.name} — "
            f"-{self.deduction_pct}% / ₦{self.repair_cost_ngn:,} repair"
        )


class SwapEstimate(models.Model):
    """
    Logged estimate session — used for analytics and price tuning.

    net_amount_ngn = (to_value − from_value_after_deductions) + total_repair_cost + service_fee
    Positive → customer pays to upgrade.
    Negative → customer receives cashback (downgrade).
    """

    session_key = models.CharField(max_length=40, db_index=True)
    from_storage = models.ForeignKey(
        StorageVariant, on_delete=models.PROTECT, related_name="swap_from"
    )
    to_storage = models.ForeignKey(
        StorageVariant, on_delete=models.PROTECT, related_name="swap_to"
    )
    defects = models.ManyToManyField(DefectType, blank=True)

    # Computed and snapshotted at estimate time so historical records are stable
    # even when admin updates base values or repair costs later.
    from_base_value_ngn = models.PositiveIntegerField(
        help_text="Snapshot of from_storage.swap_in_value_ngn at estimate time.",
    )
    from_value_ngn = models.PositiveIntegerField(
        help_text="Trade-in value after all deductions applied.",
    )
    total_repair_cost_ngn = models.PositiveIntegerField(
        default=0,
        help_text="Sum of repair_cost_ngn for all declared defects on this model.",
    )
    to_value_ngn = models.PositiveIntegerField(
        help_text="Snapshot of to_storage.uk_end_user_price_ngn at estimate time.",
    )
    service_fee_ngn = models.PositiveIntegerField(
        help_text="Flat service charge at time of estimate (from settings.SWAP_SERVICE_FEE_NGN).",
    )
    net_amount_ngn = models.IntegerField(
        help_text="Positive = customer pays; negative = customer receives cashback.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_storage} → {self.to_storage} ({self.created_at:%Y-%m-%d})"
