# Generated by Django 5.1.3 on 2024-12-14 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_rename_make_vehicle_owner_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='other_details',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='service_date',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='servicing_details',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='contact_number',
            field=models.CharField(default='0000000000', max_length=15),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='part',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='registration_number',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
