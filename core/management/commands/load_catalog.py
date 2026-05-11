"""
Management command to seed the iPhone catalog.

Usage:
    python manage.py load_catalog
    python manage.py load_catalog --csv path/to/custom.csv
    python manage.py load_catalog --clear   # wipe existing data first

The CSV only needs a uk_reseller_price_ngn column — all other prices are
derived automatically via StorageVariant.save().
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

        created_series = created_models = created_storage = updated_storage = 0

        with csv_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                series, s_new = IphoneSeries.objects.get_or_create(
                    name=row["series_name"],
                    defaults={"order": int(row["series_order"]), "is_active": True},
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

                uk_reseller = int(row["uk_reseller_price_ngn"])

                storage, sv_new = StorageVariant.objects.get_or_create(
                    model=model,
                    capacity=row["capacity"],
                    defaults={
                        # Only the source-of-truth field is needed here.
                        # save() will derive uk_end, swap_in, ng_reseller, ng_end.
                        "uk_reseller_price_ngn": uk_reseller,
                        "is_active": True,
                    },
                )
                if sv_new:
                    created_storage += 1
                elif storage.uk_reseller_price_ngn != uk_reseller:
                    # UK price changed — update it; save() recomputes derived fields.
                    storage.uk_reseller_price_ngn = uk_reseller
                    storage.save()
                    updated_storage += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done — series: {created_series} created | "
            f"models: {created_models} created | "
            f"storage variants: {created_storage} created, {updated_storage} updated"
        ))
