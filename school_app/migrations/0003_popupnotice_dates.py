# Generated migration for PopupNotice start_date and end_date fields

from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [
    ('school_app', '0001_initial'),
]

    operations = [
        migrations.AddField(
            model_name='popupnotice',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='popupnotice',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
