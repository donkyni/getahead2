# Generated by Django 5.0.1 on 2024-09-10 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('affiliation', '0020_alter_user_balances_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='palier_recommence',
            field=models.IntegerField(default=0),
        ),
    ]