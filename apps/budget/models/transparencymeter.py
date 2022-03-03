from django.db import models

COUNTRY_CHOICES = (
    ('AO', 'Angola'),
    ('CV', 'Cabo-Verde'),
    ('MZ', 'Mozambique'),
    ('ST', 'São Tomé e Principe'),
    ('GW', 'Guiné-Bissau'),
    ('TL', 'Timor-Leste')
)


class TransparenciMeter(models.Model):
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    year = models.SmallIntegerField(max_length=4)

    def __str__(self):
        return self.country



