# Generated by Django 5.0.1 on 2024-02-13 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(max_length=15, null=True, unique=True),
        ),
    ]
