# Generated by Django 3.0.8 on 2021-02-17 20:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('budget', '0011_auto_20210217_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_type', models.CharField(choices=[('new_category', 'new category'), ('update', 'update')], editable=False, max_length=20)),
                ('object_id', models.PositiveIntegerField(editable=False)),
                ('category_name', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='category')),
                ('field', models.CharField(blank=True, editable=False, max_length=40, null=True, verbose_name='field')),
                ('old_value', models.FloatField(blank=True, editable=False, null=True, verbose_name='old value')),
                ('new_value', models.FloatField(blank=True, editable=False, null=True, verbose_name='new value')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
                ('upload', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='budget.Upload', verbose_name='upload')),
            ],
        ),
    ]
