from django.core.management.base import BaseCommand
from apps.geo.models import Country


class Command(BaseCommand):
    help = "Creates PALOP-TL countries"

    def handle(self, *args, **options):
        countries = [
            {'name': "Angola", 'slug': 'angola', 'currency': 'AOA'},
            {'name': "Cabo Verde", 'slug': 'cabo-verde', 'currency': 'CVE'},
            {'name': "Guinea Bissau", 'slug': 'guinea-bissau', 'currency': 'XOF'},
            {'name': "Mozambique", 'slug': 'mozambique', 'currency': 'MZN'},
            {'name': "São Tomé e Príncipe", 'slug': 'sao-tome-e-principe', 'currency': 'STD'},
            {'name': "Timor Leste", 'slug': 'timor-leste', 'currency': 'USD'},
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
            country.currency = c['currency']
            country.save()

        print("=== FINISHED ===")
