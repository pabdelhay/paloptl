# Generated by Django 3.0.8 on 2021-05-19 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0014_auto_20210507_1837'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='upload',
            options={'ordering': ['uploaded_on']},
        ),
        migrations.AddField(
            model_name='budget',
            name='output_file',
            field=models.FileField(blank=True, editable=False, help_text='Auto generated CSV file with all data from budget.', null=True, upload_to='exports'),
        ),
        migrations.AlterField(
            model_name='upload',
            name='status',
            field=models.CharField(choices=[('validating', 'Validating'), ('importing', 'Importing'), ('success', 'Success'), ('validation_error', 'Validation error'), ('import_error', 'Import error'), ('waiting_reimport', 'Waiting reimport')], editable=False, max_length=20, verbose_name='status'),
        ),
    ]
