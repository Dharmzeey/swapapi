from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DefectPricing, DefectType, IphoneModel, IphoneSeries, StorageVariant, SwapEstimate
from .serializers import (
    DefectTypeSerializer,
    EstimateRequestSerializer,
    IphoneModelSerializer,
    IphoneSeriesSerializer,
    StorageVariantSerializer,
)


class SeriesListView(generics.ListAPIView):
    """
    GET /api/series/
    Returns all active iPhone series ordered by release generation.
    """
    serializer_class = IphoneSeriesSerializer

    def get_queryset(self):
        return IphoneSeries.objects.filter(is_active=True)


class ModelListView(generics.ListAPIView):
    """
    GET /api/models/<series_id>/
    Returns active models belonging to the given series.
    404 if the series doesn't exist or is inactive.
    """
    serializer_class = IphoneModelSerializer

    def get_queryset(self):
        return IphoneModel.objects.filter(
            series_id=self.kwargs["series_id"],
            series__is_active=True,
            is_active=True,
        ).select_related("series")


class StorageListView(generics.ListAPIView):
    """
    GET /api/storage/<model_id>/
    Returns active storage variants for the given model.
    """
    serializer_class = StorageVariantSerializer

    def get_queryset(self):
        return StorageVariant.objects.filter(
            model_id=self.kwargs["model_id"],
            model__is_active=True,
            is_active=True,
        ).select_related("model")


class DefectListView(generics.ListAPIView):
    """
    GET /api/defects/
    Returns full active defect catalogue grouped by category.
    Called once on page load; the client caches the result.
    """
    serializer_class = DefectTypeSerializer

    def get_queryset(self):
        return DefectType.objects.filter(is_active=True)


class EstimateView(APIView):
    """
    POST /api/estimate/

    Request body:
        {
            "from_storage_id": 12,
            "to_storage_id":   34,
            "defect_ids":      [1, 3, 5]   // optional, defaults to []
        }

    Pricing logic
    -------------
    For each declared defect on the swap-from phone:
      1. Look up DefectPricing(defect, from_model).
         If an active row exists → use its deduction_pct and repair_cost_ngn.
         If not → fall back to defect.default_deduction_pct, repair_cost = 0.

    from_value  = base_value × ∏(1 − deduction_i / 100)   (multiplicative)
    repair_total = Σ repair_cost_i
    net          = (to_value − from_value) + repair_total + service_fee
                   positive → customer pays (upgrade)
                   negative → customer receives cashback (downgrade)

    Response body:
        {
            "from_device":          "iPhone 13 Pro Max · 256GB",
            "from_base_value_ngn":  700000,
            "from_value_ngn":       532000,
            "to_device":            "iPhone 16 · 128GB",
            "to_value_ngn":         950000,
            "repair_breakdown":     [
                {"defect": "Cracked screen", "deduction_pct": "18.00", "repair_cost_ngn": 85000},
                {"defect": "Battery replaced", "deduction_pct": "5.00",  "repair_cost_ngn": 0}
            ],
            "total_repair_cost_ngn": 85000,
            "service_fee_ngn":       10000,
            "net_ngn":               513000,
            "direction":             "upgrade",
            "defects_applied":       ["Cracked screen", "Battery replaced"]
        }
    """

    def post(self, request):
        req = EstimateRequestSerializer(data=request.data)
        if not req.is_valid():
            return Response(req.errors, status=status.HTTP_400_BAD_REQUEST)

        data = req.validated_data

        from_storage = (
            StorageVariant.objects
            .select_related("model__series")
            .get(pk=data["from_storage_id"])
        )
        to_storage = (
            StorageVariant.objects
            .select_related("model__series")
            .get(pk=data["to_storage_id"])
        )
        defects = list(
            DefectType.objects.filter(pk__in=data["defect_ids"], is_active=True)
        ) if data["defect_ids"] else []

        # ── Pricing calculation ───────────────────────────────────────────────
        from_value = from_storage.base_value_ngn
        total_repair_cost = 0
        repair_breakdown = []

        for defect in defects:
            try:
                pricing = DefectPricing.objects.get(
                    defect=defect,
                    iphone_model=from_storage.model,
                    is_active=True,
                )
                deduction_pct = pricing.deduction_pct
                repair_cost = pricing.repair_cost_ngn
            except DefectPricing.DoesNotExist:
                deduction_pct = defect.default_deduction_pct
                repair_cost = 0

            from_value = round(from_value * (100 - deduction_pct) / 100)
            total_repair_cost += repair_cost
            repair_breakdown.append({
                "defect": defect.name,
                "deduction_pct": deduction_pct,
                "repair_cost_ngn": repair_cost,
            })

        from_value_int = from_value
        to_value = to_storage.base_value_ngn
        service_fee = int(getattr(settings, "SWAP_SERVICE_FEE_NGN", 10_000))
        net = (to_value - from_value_int) + total_repair_cost + service_fee

        direction = "upgrade" if net > 0 else "downgrade" if net < 0 else "even"

        # ── Persist the estimate ──────────────────────────────────────────────
        session_key = request.session.session_key or ""
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        estimate = SwapEstimate.objects.create(
            session_key=session_key,
            from_storage=from_storage,
            to_storage=to_storage,
            from_base_value_ngn=from_storage.base_value_ngn,
            from_value_ngn=from_value_int,
            total_repair_cost_ngn=total_repair_cost,
            to_value_ngn=to_value,
            service_fee_ngn=service_fee,
            net_amount_ngn=net,
        )
        estimate.defects.set(defects)

        # ── Response ──────────────────────────────────────────────────────────
        return Response({
            "from_device": str(from_storage),
            "from_base_value_ngn": from_storage.base_value_ngn,
            "from_value_ngn": from_value_int,
            "to_device": str(to_storage),
            "to_value_ngn": to_value,
            "repair_breakdown": repair_breakdown,
            "total_repair_cost_ngn": total_repair_cost,
            "service_fee_ngn": service_fee,
            "net_ngn": net,
            "direction": direction,
            "defects_applied": [d.name for d in defects],
        })
