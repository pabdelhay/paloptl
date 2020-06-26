from celery import task
from django.utils import timezone
from django.utils.text import slugify

from apps.geo.models import Country


@task
def test_celery():
    now = timezone.now()
    name = f"test country {now.hour}:{now.minute}"

    country = Country.objects.create(name=name, slug=slugify(name))
    return country.id
