from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_app', '0005_alter_admissionapplication_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('achievement_type', models.CharField(choices=[('student', 'Student Achievement'), ('school', 'School / College Achievement')], default='student', max_length=20)),
                ('achievement_type_display', models.CharField(blank=True, max_length=255)),
                ('student_name', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='achievements/')),
                ('achievement_date', models.DateField(blank=True, null=True)),
                ('rank_or_position', models.CharField(blank=True, max_length=255)),
                ('event_name', models.CharField(blank=True, max_length=255)),
                ('location', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'Achievement',
                'verbose_name_plural': 'Achievements',
                'ordering': ['display_order', '-achievement_date', '-created_at'],
            },
        ),
    ]
