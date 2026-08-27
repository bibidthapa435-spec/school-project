# Generated migration for AdmissionApplication and ContactMessage enhancements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_app', '0003_popupnotice_dates'),
    ]

    operations = [
        # AdmissionApplication enhancements
        migrations.AddField(
            model_name='admissionapplication',
            name='application_id',
            field=models.CharField(max_length=20, unique=True, editable=False),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='dob',
            field=models.DateField(),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='gender',
            field=models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')]),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='father_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='mother_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='email',
            field=models.EmailField(blank=True),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='previous_school',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='photo',
            field=models.ImageField(upload_to='admissions/photos/', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='documents',
            field=models.FileField(upload_to='admissions/documents/', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='admissionapplication',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='admissionapplication',
            name='status',
            field=models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending'),
        ),
        migrations.AlterField(
            model_name='admissionapplication',
            name='address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='admissionapplication',
            name='phone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='admissionapplication',
            name='class_applying',
            field=models.CharField(max_length=50),
        ),
        migrations.RemoveField(
            model_name='admissionapplication',
            name='parent_name',
        ),
        
        # ContactMessage enhancements
        migrations.AddField(
            model_name='contactmessage',
            name='phone',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='status',
            field=models.CharField(max_length=20, choices=[('unread', 'Unread'), ('read', 'Read'), ('replied', 'Replied')], default='unread'),
        ),
        migrations.AlterField(
            model_name='contactmessage',
            name='email',
            field=models.EmailField(blank=True),
        ),
        migrations.AlterField(
            model_name='contactmessage',
            name='subject',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='contactmessage',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]