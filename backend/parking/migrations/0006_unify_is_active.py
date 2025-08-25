from django.db import migrations, models

def forward(apps, schema_editor):
    ParkingFacility = apps.get_model("parking", "ParkingFacility")
    ParkingSpot = apps.get_model("parking", "ParkingSpot")

    # if is_archived existed, migrate its value
    if hasattr(ParkingFacility, "is_archived"):
        for f in ParkingFacility.objects.all():
            if getattr(f, "is_archived", False):
                f.is_active = False
                f.save(update_fields=["is_active"])

    if hasattr(ParkingSpot, "is_archived"):
        for s in ParkingSpot.objects.all():
            if getattr(s, "is_archived", False):
                s.is_active = False
                s.save(update_fields=["is_active"])

def reverse(apps, schema_editor):
    # safe no-op rollback
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("parking", "0005_spotpredictionlog_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="parkingfacility",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="parkingspot",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(forward, reverse),
        # optional: remove is_archived if present
        migrations.RemoveField(
            model_name="parkingfacility",
            name="is_archived",
        ),
        migrations.RemoveField(
            model_name="parkingspot",
            name="is_archived",
        ),
    ]
