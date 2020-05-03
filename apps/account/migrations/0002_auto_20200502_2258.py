# Generated by Django 3.0.5 on 2020-05-03 01:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_auto_20200502_2258'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Dados', 'verbose_name_plural': 'Dados'},
        ),
        migrations.AlterField(
            model_name='profile',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='geo.Country', verbose_name='país'),
        ),
    ]
