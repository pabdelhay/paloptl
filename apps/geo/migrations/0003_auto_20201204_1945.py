# Generated by Django 3.0.8 on 2020-12-04 22:45

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_country_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='currency',
            field=djmoney.models.fields.CurrencyField(choices=[('AOA', 'AOA Kz'), ('CVE', 'CVE $'), ('MZN', 'MZN MT'), ('STD', 'STD Db'), ('USD', 'USD $'), ('XOF', 'XOF (CFA)')], default='XYZ', max_length=3, verbose_name='currency'),
        ),
    ]
