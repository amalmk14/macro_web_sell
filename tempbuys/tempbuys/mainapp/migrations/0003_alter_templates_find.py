# Generated by Django 4.1.2 on 2023-11-06 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_templates_find'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templates',
            name='find',
            field=models.CharField(max_length=50),
        ),
    ]