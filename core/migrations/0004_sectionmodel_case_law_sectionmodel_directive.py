from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_searchhistorymodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectionmodel',
            name='case_law',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sectionmodel',
            name='directive',
            field=models.TextField(blank=True, null=True),
        ),
    ]
