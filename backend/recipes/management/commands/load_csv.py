import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load data from CSV files into the database'

    def handle(self, *args, **options):
        csv_path = os.path.join(os.getcwd(), 'data', 'ingredients.csv')
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip()
                )
            self.stdout.write(
                self.style.SUCCESS('Ingredients loaded successfully')
            )
