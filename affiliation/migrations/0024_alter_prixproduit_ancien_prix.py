# Generated by Django 5.0.1 on 2024-09-11 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('affiliation', '0023_prixproduit_ancien_prix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prixproduit',
            name='ancien_prix',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True),
        ),
    ]