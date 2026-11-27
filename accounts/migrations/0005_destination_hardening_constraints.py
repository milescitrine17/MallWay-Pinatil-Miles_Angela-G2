# Generated for PD3 Hardening: validators, unique constraint, and index on Destination

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_destination_created_by_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destination',
            name='floor',
            field=models.CharField(
                max_length=50,
                validators=[django.core.validators.MinLengthValidator(2, message='Floor must be at least 2 characters.')],
            ),
        ),
        migrations.AlterField(
            model_name='destination',
            name='location',
            field=models.CharField(
                max_length=150,
                validators=[django.core.validators.MinLengthValidator(2, message='Location / Unit must be at least 2 characters.')],
            ),
        ),
        migrations.AlterField(
            model_name='destination',
            name='name',
            field=models.CharField(
                max_length=150,
                validators=[django.core.validators.MinLengthValidator(2, message='Destination name must be at least 2 characters.')],
            ),
        ),
        migrations.AddIndex(
            model_name='destination',
            index=models.Index(fields=['archived', 'featured'], name='dest_archived_featured_idx'),
        ),
        migrations.AddConstraint(
            model_name='destination',
            constraint=models.UniqueConstraint(
                fields=('name', 'floor', 'location'),
                name='unique_destination_name_floor_location',
            ),
        ),
    ]
