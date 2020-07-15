from django.core.management.base import BaseCommand
from apps.geo.models import Country


class Command(BaseCommand):
    help = "Creates PALOP-TL countries"

    def handle(self, *args, **options):
        countries = [
            {'name': "Angola", 'slug': 'angola'},
            {'name': "Cabo Verde", 'slug': 'cabo-verde'},
            {'name': "Guinea Bissau", 'slug': 'guinea-bissau'},
            {'name': "Mozambique", 'slug': 'mozambique'},
            {'name': "São Tomé e Príncipe", 'slug': 'sao-tome-e-principe'},
            {'name': "Timor Leste", 'slug': 'timor-leste'},
        ]
        print("Creating Palop-TL countries...")
        for c in countries:
            try:
                country = Country.objects.get(slug=c['slug'])
                print(f"{c['name']} already registered.")
            except:
                country = Country(**c)
                print(f"Creating {c['name']}.")
            if not bool(country.flag):
                country.flag = f"countries/{c['slug']}.png"
            country.save()

        print("=== FINISHED ===")
