# Generated by Django 5.0.1 on 2024-10-27 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('affiliation', '0028_alter_user_don_bam_alter_user_don_maya_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payement',
            name='statut',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
