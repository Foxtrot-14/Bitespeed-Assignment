# Generated by Django 5.0.2 on 2024-03-02 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_alter_customer_linkedid'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
