# Generated by Django 5.1.4 on 2025-01-15 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management_system', '0003_alter_milestone_payment_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='milestone',
            old_name='payment_amount',
            new_name='payable_amount',
        ),
    ]
