from rest_framework import serializers

from .models import DefectType, IphoneModel, IphoneSeries, StorageVariant


class IphoneSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = IphoneSeries
        fields = ("id", "name", "order")


class IphoneModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = IphoneModel
        fields = ("id", "name", "slug", "variant_type", "order")


class StorageVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageVariant
        fields = ("id", "capacity", "swap_in_value_ngn")


class DefectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectType
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "category",
            "default_deduction_pct",
            "applies_to_view",
            "order",
        )


# ── Estimate ──────────────────────────────────────────────────────────────────

class EstimateRequestSerializer(serializers.Serializer):
    from_storage_id = serializers.IntegerField()
    to_storage_id = serializers.IntegerField()
    defect_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
        required=False,
        default=list,
    )

    def validate_from_storage_id(self, value):
        if not StorageVariant.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Storage variant not found or inactive.")
        return value

    def validate_to_storage_id(self, value):
        if not StorageVariant.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Storage variant not found or inactive.")
        return value

    def validate_defect_ids(self, value):
        if value:
            found = DefectType.objects.filter(pk__in=value, is_active=True).count()
            if found != len(set(value)):
                raise serializers.ValidationError(
                    "One or more defect IDs are invalid or inactive."
                )
        return value
