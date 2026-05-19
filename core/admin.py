from django.contrib import admin

from .models import (
    DefectPricing,
    DefectType,
    IphoneModel,
    IphoneSeries,
    StorageVariant,
    SwapEstimate,
)


# ── Inlines ──────────────────────────────────────────────────────────────────

class StorageVariantInline(admin.TabularInline):
    model = StorageVariant
    extra = 1
    fields = ("capacity", "swap_in_value_ngn", "uk_end_user_price_ngn", "is_active")


class DefectPricingByModelInline(admin.TabularInline):
    """Shows per-defect repair costs when viewing an IphoneModel."""
    model = DefectPricing
    extra = 0
    fields = ("defect", "deduction_pct", "repair_cost_ngn", "is_active")
    autocomplete_fields = ("defect",)
    verbose_name = "Defect pricing"
    verbose_name_plural = "Defect pricing (repair costs for this model)"


class DefectPricingByDefectInline(admin.TabularInline):
    """Shows per-model repair costs when viewing a DefectType."""
    model = DefectPricing
    extra = 0
    fields = ("iphone_model", "deduction_pct", "repair_cost_ngn", "is_active")
    autocomplete_fields = ("iphone_model",)
    verbose_name = "Model pricing"
    verbose_name_plural = "Per-model pricing (repair cost per iPhone model)"


# ── Model admins ─────────────────────────────────────────────────────────────

@admin.register(IphoneSeries)
class IphoneSeriesAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)


@admin.register(IphoneModel)
class IphoneModelAdmin(admin.ModelAdmin):
    list_display = ("name", "series", "variant_type", "order", "is_active")
    list_filter = ("series", "variant_type", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [StorageVariantInline, DefectPricingByModelInline]


@admin.register(StorageVariant)
class StorageVariantAdmin(admin.ModelAdmin):
    list_display = ("model", "capacity", "swap_in_value_ngn", "uk_end_user_price_ngn", "ng_end_user_price_ngn", "is_active")
    list_filter = ("model__series", "capacity", "is_active")
    list_editable = ("swap_in_value_ngn", "uk_end_user_price_ngn", "is_active")
    search_fields = ("model__name",)


@admin.register(DefectType)
class DefectTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "default_deduction_pct", "applies_to_view", "order", "is_active")
    list_filter = ("category", "applies_to_view", "is_active")
    list_editable = ("default_deduction_pct", "order", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [DefectPricingByDefectInline]


@admin.register(DefectPricing)
class DefectPricingAdmin(admin.ModelAdmin):
    list_display = ("defect", "iphone_model", "deduction_pct", "repair_cost_ngn", "is_active")
    list_filter = ("iphone_model__series", "defect__category", "is_active")
    list_editable = ("deduction_pct", "repair_cost_ngn", "is_active")
    search_fields = ("defect__name", "iphone_model__name")
    autocomplete_fields = ("defect", "iphone_model")


@admin.register(SwapEstimate)
class SwapEstimateAdmin(admin.ModelAdmin):
    list_display = (
        "from_storage", "to_storage",
        "from_base_value_ngn", "from_value_ngn",
        "total_repair_cost_ngn", "to_value_ngn",
        "net_amount_ngn", "created_at",
    )
    list_filter = ("created_at",)
    readonly_fields = (
        "session_key", "from_storage", "to_storage", "defects",
        "from_base_value_ngn", "from_value_ngn", "total_repair_cost_ngn",
        "to_value_ngn", "service_fee_ngn", "net_amount_ngn", "created_at",
    )
    filter_horizontal = ("defects",)
