# Generated by Django 3.1 on 2024-04-12 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20240411_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='postal_code',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]