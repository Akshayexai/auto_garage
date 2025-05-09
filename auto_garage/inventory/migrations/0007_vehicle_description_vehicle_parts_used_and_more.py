# Generated by Django 5.1.3 on 2024-12-15 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_remove_bill_parts_rename_service_date_bill_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='parts_used',
            field=models.ManyToManyField(blank=True, to='inventory.part'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='registration_number',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
