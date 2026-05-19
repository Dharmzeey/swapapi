"""
Management command to seed defect types and per-model defect pricing.

Usage:
    python manage.py load_defects
    python manage.py load_defects --types-csv path/to/defect_types.csv \\
                                  --pricing-csv path/to/defect_pricing.csv
    python manage.py load_defects --clear
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from core.models import DefectPricing, DefectType, IphoneModel

DATA = Path(__file__).resolve().parents[3] / "data"


class Command(BaseCommand):
    help = "Load defect types and per-model defect pricing from CSV files."

    def add_arguments(self, parser):
        parser.add_argument("--types-csv",   default=str(DATA / "defect_types.csv"))
        parser.add_argument("--pricing-csv", default=str(DATA / "defect_pricing.csv"))
        parser.add_argument("--clear", action="store_true",
                            help="Delete all existing defect data before loading.")

    def handle(self, *args, **options):
        if options["clear"]:
            DefectPricing.objects.all().delete()
            DefectType.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing defect data."))

        # ── 1. Defect types ───────────────────────────────────────────────────
        types_path = Path(options["types_csv"])
        created_types = updated_types = 0

        with types_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                obj, created = DefectType.objects.update_or_create(
                    slug=row["slug"],
                    defaults={
                        "name":                  row["name"],
                        "category":              row["category"],
                        "default_deduction_pct": int(row["default_deduction_pct"]),
                        "description":           row["description"],
                        "applies_to_view":       row["applies_to_view"],
                        "order":                 int(row["order"]),
                        "is_active":             True,
                    },
                )
                if created:
                    created_types += 1
                else:
                    updated_types += 1

        self.stdout.write(
            f"Defect types — {created_types} created, {updated_types} updated"
        )

        # ── 2. Defect pricing ─────────────────────────────────────────────────
        pricing_path = Path(options["pricing_csv"])
        created_pricing = updated_pricing = skipped = 0

        # Cache lookups to avoid repeated DB hits
        defect_cache = {d.slug: d for d in DefectType.objects.all()}
        model_cache  = {m.slug: m for m in IphoneModel.objects.all()}

        with pricing_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                defect = defect_cache.get(row["defect_slug"])
                model  = model_cache.get(row["model_slug"])

                if not defect or not model:
                    self.stderr.write(
                        f"  skip: defect={row['defect_slug']} model={row['model_slug']} not found"
                    )
                    skipped += 1
                    continue

                obj, created = DefectPricing.objects.update_or_create(
                    defect=defect,
                    iphone_model=model,
                    defaults={
                        "deduction_pct":   int(row["deduction_pct"]),
                        "repair_cost_ngn": int(row["repair_cost_ngn"]),
                        "is_active":       True,
                    },
                )
                if created:
                    created_pricing += 1
                else:
                    updated_pricing += 1

        self.stdout.write(self.style.SUCCESS(
            f"Defect pricing — {created_pricing} created, {updated_pricing} updated"
            + (f", {skipped} skipped" if skipped else "")
        ))
