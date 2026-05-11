"""
Management command to seed the iPhone catalog from data/iphone_catalog.csv.

Usage:
    python manage.py load_catalog
    python manage.py load_catalog --csv path/to/custom.csv
    python manage.py load_catalog --clear   # wipe existing data first
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from core.models import IphoneModel, IphoneSeries, StorageVariant


class Command(BaseCommand):
    help = "Load iPhone series, models and storage variants from the catalog CSV."

    DEFAULT_CSV = Path(__file__).resolve().parents[3] / "data" / "iphone_catalog.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=str(self.DEFAULT_CSV),
            help="Path to the CSV file (default: data/iphone_catalog.csv)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing series, models and storage variants before loading.",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV not found: {csv_path}"))
            return

        if options["clear"]:
            StorageVariant.objects.all().delete()
            IphoneModel.objects.all().delete()
            IphoneSeries.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing catalog data."))

        created_series = created_models = created_storage = 0
        updated_storage = 0

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                series, s_new = IphoneSeries.objects.get_or_create(
                    name=row["series_name"],
                    defaults={
                        "order": int(row["series_order"]),
                        "is_active": True,
                    },
                )
                if s_new:
                    created_series += 1

                model, m_new = IphoneModel.objects.get_or_create(
                    slug=row["model_slug"],
                    defaults={
                        "series": series,
                        "name": row["model_name"],
                        "variant_type": row["variant_type"],
                        "order": int(row["model_order"]),
                        "is_active": True,
                    },
                )
                if m_new:
                    created_models += 1

                storage, sv_new = StorageVariant.objects.get_or_create(
                    model=model,
                    capacity=row["capacity"],
                    defaults={
                        "swap_in_value_ngn": int(row["swap_in_value_ngn"]),
                        "uk_end_user_price_ngn": int(row["uk_end_user_price_ngn"]),
                        "uk_reseller_price_ngn": int(row["uk_reseller_price_ngn"]) if row["uk_reseller_price_ngn"] else None,
                        "ng_end_user_price_ngn": int(row["ng_end_user_price_ngn"]) if row["ng_end_user_price_ngn"] else None,
                        "ng_reseller_price_ngn": int(row["ng_reseller_price_ngn"]) if row["ng_reseller_price_ngn"] else None,
                        "is_active": True,
                    },
                )
                if sv_new:
                    created_storage += 1
                else:
                    # Update prices if any changed in the CSV
                    new_swap_in = int(row["swap_in_value_ngn"])
                    new_uk_end = int(row["uk_end_user_price_ngn"])
                    new_uk_res = int(row["uk_reseller_price_ngn"]) if row["uk_reseller_price_ngn"] else None
                    new_ng_end = int(row["ng_end_user_price_ngn"]) if row["ng_end_user_price_ngn"] else None
                    new_ng_res = int(row["ng_reseller_price_ngn"]) if row["ng_reseller_price_ngn"] else None
                    changed = (
                        storage.swap_in_value_ngn != new_swap_in
                        or storage.uk_end_user_price_ngn != new_uk_end
                        or storage.uk_reseller_price_ngn != new_uk_res
                        or storage.ng_end_user_price_ngn != new_ng_end
                        or storage.ng_reseller_price_ngn != new_ng_res
                    )
                    if changed:
                        storage.swap_in_value_ngn = new_swap_in
                        storage.uk_end_user_price_ngn = new_uk_end
                        storage.uk_reseller_price_ngn = new_uk_res
                        storage.ng_end_user_price_ngn = new_ng_end
                        storage.ng_reseller_price_ngn = new_ng_res
                        storage.save(update_fields=[
                            "swap_in_value_ngn",
                            "uk_end_user_price_ngn",
                            "uk_reseller_price_ngn",
                            "ng_end_user_price_ngn",
                            "ng_reseller_price_ngn",
                        ])
                        updated_storage += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done — series: {created_series} created | "
            f"models: {created_models} created | "
            f"storage variants: {created_storage} created, {updated_storage} updated"
        ))
