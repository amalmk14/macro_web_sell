# Generated by Django 4.1.2 on 2023-11-06 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='templates',
            name='find',
            field=models.CharField(default=1, max_length=50, unique=True),
            preserve_default=False,
        ),
    ]