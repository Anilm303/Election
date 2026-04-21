# Generated migration to add allow_voting field to Election model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_alter_votelog_activity_type_alter_votelog_election'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='allow_voting',
            field=models.BooleanField(default=True),
        ),
    ]
