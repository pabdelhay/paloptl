from django import forms

from apps.budget.models.transparencymeter import transparencymeter

COUNTRY_CHOICES = (
    ('AO', 'Angola'),
    ('CV', 'Cabo-Verde'),
    ('MZ', 'Mozambique'),
    ('ST', 'São Tomé e Principe'),
    ('GW', 'Guiné-Bissau'),
    ('TL', 'Timor-Leste')
)


class TransForm(forms.ModelForm):
    class Meta:
        model = transparencymeter
        fields = "__all__"
