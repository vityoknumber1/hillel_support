# Generated by Django 4.2.2 on 2023-06-25 20:12

from django.db import migrations, models

import tickets.constants


class Migration(migrations.Migration):
    dependencies = [
        ("tickets", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=tickets.constants.TicketStatus["NOT_STARTED"]
            ),
        ),
    ]
