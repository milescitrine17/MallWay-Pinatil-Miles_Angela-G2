import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_destination_alter_profile_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="destination",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="destination_images/"),
        ),
        migrations.AddField(
            model_name="destination",
            name="created_by",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="destinations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="destination",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="destination",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name="destination",
            options={"ordering": ["name"]},
        ),
    ]
