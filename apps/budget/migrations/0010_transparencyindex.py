# Generated by Django 3.0.8 on 2021-02-17 16:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0003_auto_20201204_1945'),
        ('budget', '0009_auto_20210211_2357'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransparencyIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='year')),
                ('score_open_data', models.SmallIntegerField(blank=True, help_text='0 - 100', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='score - open data')),
                ('score_reports', models.SmallIntegerField(blank=True, help_text='0 - 100', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='score - reports')),
                ('score_data_quality', models.SmallIntegerField(blank=True, help_text='0 - 200', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(200)], verbose_name='score - data quality')),
                ('transparency_index', models.SmallIntegerField(blank=True, help_text='0 - 100', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='transparency index')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='index', to='geo.Country', verbose_name='country')),
            ],
            options={
                'verbose_name': 'transparency index',
                'verbose_name_plural': 'transparency index',
                'ordering': ['country', '-year'],
                'unique_together': {('country', 'year')},
            },
        ),
    ]
