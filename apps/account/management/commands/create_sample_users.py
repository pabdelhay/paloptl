from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand, CommandError

from apps.geo.models import Country


class Command(BaseCommand):
    help = "Creates an admin user if no users are present in the current database."

    def handle(self, *args, **options):
        # Skip django-guardian AnonymousUser that is created by the initial migrations.
        for c in Country.objects.all():
            fields = {
                'username': f"user_{c.slug}".lower(),
                'first_name': "CSO member",
                'last_name': "CSO member",
                'is_staff': True,
                'is_active': True,
                'password': make_password('PalopTLtests')
            }
            try:
                user = User.objects.get(slug=fields['username'])
            except User.DoesNotExist:
                user = User.objects.create(**fields)
                group = Group.objects.get(name='CSO team')

