# Generated by Django 5.0.1 on 2024-09-25 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('affiliation', '0025_payement_statut_alter_historiquevente_statut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='sexe',
            field=models.CharField(blank=True, choices=[('Homme', 'Homme'), ('Femme', 'Femme')], max_length=120, null=True),
        ),
    ]