import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_sectionmodel_case_law_sectionmodel_directive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='email',
            field=models.EmailField(max_length=254, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='phone',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name='PhoneOTPModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('phone', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=6)),
                ('expires_at', models.DateTimeField(blank=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Phone OTP',
                'verbose_name_plural': 'Phone OTPs',
                'db_table': 'phone_otps',
            },
        ),
    ]
